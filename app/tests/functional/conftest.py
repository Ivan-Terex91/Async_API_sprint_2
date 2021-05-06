import asyncio
from dataclasses import dataclass
from functools import partial

import aiohttp
import pytest
from aioredis import create_redis
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy

SERVICE_URL = "http://127.0.0.1:8000"
GENRE_PREFIX = "/api/v1/genre"


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
async def es_client():
    client = AsyncElasticsearch(hosts="127.0.0.1:9200")
    yield client
    await client.close()


@pytest.fixture(scope="session")
async def redis_client():
    client = await create_redis(address="127.0.0.1:6379")
    yield client
    await client.close()


@pytest.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(session):
    async def inner(prefix: str, method: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = "".join((SERVICE_URL, prefix, method))
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture(scope="function")
async def make_genre_request(make_get_request):
    return partial(make_get_request, prefix=GENRE_PREFIX)
