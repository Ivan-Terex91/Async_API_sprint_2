import asyncio
import json
from dataclasses import dataclass
from pathlib import Path

import aiohttp
import pytest
from aioredis import create_redis
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy
from pydantic import AnyHttpUrl, BaseSettings, RedisDsn


class Settings(BaseSettings):
    api_url: AnyHttpUrl
    elastic_dsn: AnyHttpUrl
    redis_dsn: RedisDsn

    class Config:
        env_file = ".local.env"
        env_file_encoding = "utf-8"


@pytest.fixture(scope="session")
def settings():
    return Settings()


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def es_client(settings: Settings):
    indexes = {}
    indexes_dir = Path(".") / "testdata" / "indexes"
    for index_path in indexes_dir.iterdir():
        with index_path.open() as index_file:
            indexes[index_path.stem] = json.load(index_file)

    async with AsyncElasticsearch(hosts=str(settings.elastic_dsn)) as client:
        for index_name, index_data in indexes.items():
            await client.indices.create(index=index_name, body=index_data)

        yield client

        for index_name in indexes.keys():
            await client.indices.delete(index=index_name)


@pytest.fixture(scope="session")
async def redis_client(settings: Settings):
    client = await create_redis(address=str(settings.redis_dsn))
    yield client
    client.close()


@pytest.fixture(autouse=True)
async def redis_flushall(redis_client):
    """
    Очищает редис после каждого теста
    """
    yield
    await redis_client.flushall()


@pytest.fixture(scope="session")
async def http_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope="session")
def make_get_request(settings: Settings, http_session: aiohttp.ClientSession):
    async def inner(prefix: str, method: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = "".join((str(settings.api_url), prefix, method))
        async with http_session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
