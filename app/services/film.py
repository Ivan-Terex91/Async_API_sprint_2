from functools import lru_cache
from typing import Dict, Iterable, Optional

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.base import AbstractDBStorage
from db.elastic import get_elastic, get_film_storage
from models.film import Film


class FilmService:
    def __init__(self, film_storage: AbstractDBStorage):
        self.film_storage = film_storage

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        res = await self.film_storage.get(id=film_id)
        if not res:
            return None
        return Film(**res)

    async def get_page(
        self, filter_map: dict, page_number: int, page_size: int, sort_value: str, sort_order: str
    ) -> Iterable[Film]:
        res = await self.film_storage.page(
            filter_map=filter_map,
            order_map={sort_value: sort_order},
            page=page_number,
            page_size=page_size,
        )
        return (Film(**g) for g in res)

    async def search(self, page: int, size: int, match_obj: str) -> Iterable[Dict]:
        """Метод поиска фильмов по названию"""
        return await self.film_storage.page(
            search_map={"title": match_obj},
            page=page,
            page_size=size,
        )


@lru_cache()
def get_film_service(
    elastic: AsyncElasticsearch = Depends(get_elastic), film_storage=Depends(get_film_storage)
) -> FilmService:
    return FilmService(film_storage=film_storage)
