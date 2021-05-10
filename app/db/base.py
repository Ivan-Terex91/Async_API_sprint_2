from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Optional

DEFAULT_LIMIT = 50


class AbstractCacheStorage(ABC):
    """
    Абстрактный класс для взаимодействия с хранилищем для кеширования
    """

    @abstractmethod
    async def get(self, key: str) -> Any:
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire: Optional[int] = None) -> None:
        pass


class AbstractDBStorage(ABC):
    @abstractmethod
    async def get(self, id: Any) -> Optional[Dict]:
        pass

    @abstractmethod
    async def filter(
        self,
        filter_map: Optional[dict] = None,
        order_map: Optional[dict] = None,
        offset: int = 0,
        limit: int = DEFAULT_LIMIT,
        **kwargs
    ) -> Iterable[Dict]:
        pass

    async def page(
        self,
        filter_map: Optional[dict] = None,
        order_map: Optional[dict] = None,
        page: int = 1,
        page_size: int = DEFAULT_LIMIT,
        **kwargs
    ) -> Iterable[Dict]:
        return await self.filter(
            filter_map=filter_map,
            order_map=order_map,
            offset=(page - 1) * page_size,
            limit=page_size,
            **kwargs
        )
