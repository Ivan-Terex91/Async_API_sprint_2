from functools import lru_cache
from typing import Dict, List, Optional, Tuple

from fastapi import Depends

from db.base import AbstractDBStorage
from db.elastic import get_film_storage, get_person_storage
from models.person import Person, RoleType

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    """Бизнес логика получения персон."""

    def __init__(self, person_storage: AbstractDBStorage, film_storage: AbstractDBStorage):
        self.person_storage = person_storage
        self.film_storage = film_storage

    async def get_by_id(self, person_id: str) -> Optional[Tuple[Person, List[str], List[str]]]:
        """Метод получения данных о персоне."""
        person = await self.person_storage.get(id=person_id)
        if not person:
            return None, None, None

        films = await self.get_person_film_data(person_id)
        film_ids = set()
        person_roles = []
        for role, film in films.items():
            person_roles.append(role)
            film_ids.update({film_param["id"] for film_param in film})

        return Person(**person), person_roles, sorted(list(film_ids))

    async def get_person_film_list(self, person_id: str) -> Optional[List[Dict]]:
        """Метод получения списка фильмов в которых принимала участие персона."""

        person = await self.person_storage.get(person_id)
        if not person:
            return []

        films = await self.get_person_film_data(person["id"])
        person_films = {}
        for role, film in films.items():
            for film_param in film:
                if film_param["id"] not in person_films:
                    film_param["roles"] = [role]
                    person_films[film_param["id"]] = film_param
                else:
                    person_films[film_param["id"]]["roles"].append(role)
        return [film_param for film_param in person_films.values()]

    async def search_person_by_full_name(
        self, page: int, size: int, match_obj: str
    ) -> Optional[List[Tuple[Person, List[str], List[str]]]]:
        """Метод поиска персон по полному имени"""
        persons = await self.person_storage.page(
            search_map={"full_name": match_obj}, page=page, page_size=size
        )
        full_persons_data = []
        for person in persons:
            person, person_roles, film_ids = await self.get_by_id(person["id"])
            full_persons_data.append((person, person_roles, film_ids))
        return full_persons_data

    async def get_person_film_data(self, person_id: str) -> Dict:
        """Метод возвращает данные фильмов в которых учавствовала персона."""
        person_films_data = {}
        all_roles = [role.value for role in RoleType]
        for role in all_roles:
            films = await self.film_storage.filter(
                filter_map={f"{role}_id": person_id}, order_map={"id": "asc"}
            )
            if films:
                person_films_data[role] = [film for film in films]
        return person_films_data


@lru_cache()
def get_person_service(
    person_storage=Depends(get_person_storage),
    film_storage=Depends(get_film_storage),
) -> PersonService:
    return PersonService(person_storage=person_storage, film_storage=film_storage)
