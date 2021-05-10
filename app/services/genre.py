from functools import lru_cache
from typing import Iterable, Optional

from fastapi import Depends

from db.base import AbstractDBStorage
from db.elastic import get_genre_storage
from models.genre import Genre


class GenreService:
    """Бизнесс логика получения жанров"""

    def __init__(self, genre_storage: AbstractDBStorage):
        self.genre_storage = genre_storage

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        """Метод получения данных о жанре"""
        res = await self.genre_storage.get(id=genre_id)
        if not res:
            return None
        return Genre(**res)

    async def get_genres_list(
        self, page: int, size: int, sort_value: str, sort_order: str
    ) -> Iterable[Genre]:
        """Метод получения данных о списке жанров из elastic"""
        res = await self.genre_storage.page(
            order_map={sort_value: sort_order}, page=page, page_size=size
        )
        return (Genre(**g) for g in res)


@lru_cache()
def get_genre_service(
    genre_storage: AbstractDBStorage = Depends(get_genre_storage),
) -> GenreService:
    return GenreService(genre_storage=genre_storage)
