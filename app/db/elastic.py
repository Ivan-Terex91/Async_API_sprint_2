from functools import lru_cache
from typing import Dict, Iterable, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.base import DEFAULT_LIMIT, AbstractDBStorage

es: AsyncElasticsearch = None

# Функция понадобится при внедрении зависимостей
async def get_elastic() -> AsyncElasticsearch:
    return es


class ElasticStorage(AbstractDBStorage):
    def __init__(self, elastic: AsyncElasticsearch, index_name: str):
        self.elastic = elastic
        self.index_name = index_name

    async def get(self, id: str) -> Optional[Dict]:
        try:
            doc = await self.elastic.get(index=self.index_name, id=id)
        except NotFoundError:
            return None

        return doc["_source"]

    async def filter(
        self,
        filter_map: Optional[dict] = None,
        search_map: Optional[dict] = None,
        order_map: Optional[dict] = None,
        offset: int = 0,
        limit: int = DEFAULT_LIMIT,
        **kwargs,
    ) -> Iterable[Dict]:
        filter_map = filter_map or {}
        search_map = search_map or {}
        order_map = order_map or {}

        body = {}
        if filter_map or search_map:
            body["query"] = self.get_query(filter_map, search_map)

        docs = await self.elastic.search(
            index=self.index_name,
            sort=[f"{field}:{direction}" for field, direction in order_map.items()],
            from_=offset,
            size=limit,
            body=body,
        )
        return [doc["_source"] for doc in docs["hits"]["hits"]]

    def get_query(self, filter_map: Dict, search_map: Dict) -> Dict:
        query = {}

        if search_map:
            field, match_obj = list(search_map.items())[0]
            query["match"] = {field: match_obj}

        return query


class ElasticFilmStorage(ElasticStorage):
    def get_query(self, filter_map: Dict, search_map: Dict) -> Dict:
        query = super().get_query(filter_map, search_map)

        if "genre_id" in filter_map:
            query["nested"] = {
                "path": "genres",
                "query": {"term": {"genres.id": str(filter_map["genre_id"])}},
            }

        for role in ["actor", "director", "writer"]:
            key = f"{role}_id"
            if key in filter_map:
                path = f"{role}s"
                query["nested"] = {
                    "path": path,
                    "query": {"term": {f"{path}.id": str(filter_map[key])}},
                }

        return query


@lru_cache()
def get_genre_storage(elastic: AsyncElasticsearch = Depends(get_elastic)) -> ElasticStorage:
    return ElasticStorage(elastic=elastic, index_name="genres")


@lru_cache()
def get_film_storage(elastic: AsyncElasticsearch = Depends(get_elastic)) -> ElasticFilmStorage:
    return ElasticFilmStorage(elastic=elastic, index_name="movies")


@lru_cache()
def get_person_storage(elastic: AsyncElasticsearch = Depends(get_elastic)) -> ElasticStorage:
    return ElasticStorage(elastic=elastic, index_name="persons")
