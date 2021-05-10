import logging

import aioredis
import uvicorn as uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from api.v1 import film, genre, person
from core import config, json
from core.logger import LOGGING
from core.utils import async_iterator_wrapper
from db import elastic, redis
from db.base import AbstractCacheStorage
from db.redis import get_cache_storage

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


class CacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, cache_storage: AbstractCacheStorage):
        super().__init__(app)
        self.cache_storage = cache_storage

    async def dispatch(self, request: Request, call_next):
        key = request["raw_path"] + request.get("query_string", "")
        data_in_cache = await self.cache_storage.get(key=key)

        if data_in_cache:
            return ORJSONResponse(content=json.loads(data_in_cache))

        response = await call_next(request)

        if response.status_code == 307:
            return RedirectResponse(url=response.headers.get("location"))

        resp_body = [section async for section in response.__dict__["body_iterator"]]
        response.__setattr__("body_iterator", async_iterator_wrapper(resp_body))
        resp_body = resp_body[0]

        if key not in (b"/api/openapi", b"/api/openapi.json"):
            await self.cache_storage.set(key=key, value=resp_body)

        return response


@app.on_event("startup")
async def startup():
    """
    Подключаемся к базам при старте сервера
    Подключиться можем при работающем event-loop
    Поэтому логика подключения происходит в асинхронной функции
    """
    redis.redis = await aioredis.create_redis_pool(
        config.REDIS_DSN, minsize=10, maxsize=20, encoding="utf-8"
    )
    elastic.es = AsyncElasticsearch(hosts=[config.ELASTIC_DSN])

    cache_storage = await get_cache_storage()
    app.add_middleware(CacheMiddleware, cache_storage=cache_storage)


@app.on_event("shutdown")
async def shutdown():
    """
    Отключаемся от баз при выключении сервера
    """
    await redis.redis.close()
    await elastic.es.close()


# Подключаем роутер к серверу, указав префикс /v1/film
# Теги указываем для удобства навигации по документации
app.include_router(film.router, prefix="/api/v1/film", tags=["film"])
app.include_router(genre.router, prefix="/api/v1/genre", tags=["genre"])
app.include_router(person.router, prefix="/api/v1/person", tags=["person"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
