from abc import ABC, abstractmethod
from typing import Any, Optional


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
