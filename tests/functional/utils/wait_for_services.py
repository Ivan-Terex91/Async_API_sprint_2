import asyncio
import os
from socket import gaierror

import aiohttp
import aioredis
from elasticsearch import AsyncElasticsearch

API_URL = os.getenv("API_URL", "http://localhost:8000/")
REDIS_DSN = os.getenv("REDIS_DSN", "redis://localhost:6379/0")
ELASTIC_DSN = os.getenv("ELASTIC_DSN", "http://localhost:9200/")


async def wait_elastic():
    async with AsyncElasticsearch(hosts=[ELASTIC_DSN]) as elastic:
        while True:
            if await elastic.ping():
                return
            await asyncio.sleep(1)


async def wait_redis():
    async def redis_ping():
        try:
            if await redis.ping():
                return True
        except aioredis.ConnectionClosedError:
            return False

    redis = None

    while not redis:
        try:
            redis = await aioredis.create_redis(address=REDIS_DSN)
        except gaierror:
            await asyncio.sleep(1)

    try:
        while True:
            if await redis_ping():
                return
            await asyncio.sleep(1)
    except Exception:
        raise
    finally:
        redis.close()


async def wait_api():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await session.get(API_URL)
                return
            except aiohttp.client_exceptions.ClientConnectionError:
                await asyncio.sleep(1)


async def main():
    await wait_elastic()
    await wait_redis()
    await wait_api()


asyncio.run(main())
