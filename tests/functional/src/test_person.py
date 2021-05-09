import json
from functools import partial
from typing import Dict, List

import pytest

PERSON_PREFIX = "/api/v1/person"


@pytest.fixture(scope="session")
async def make_person_request(make_get_request):
    return partial(make_get_request, prefix=PERSON_PREFIX)


@pytest.fixture(scope="module", autouse=True)
async def person_data(es_client):
    persons = [
        {"id": "facfb08d-8d9a-42f3-9e4e-697d8f9d6e4a", "full_name": "Harrison Ford"},
        {"id": "b6ddf2ec-de20-4bb9-933b-5674edf70c1b", "full_name": "George Lucas"},
        {"id": "82ea4033-1ed9-4639-a52e-6454b3249a3a", "full_name": "Mark Hamill"},
        {"id": "dfdbfd96-80ec-47fb-8c12-0b33db66baf5", "full_name": "Arnold Statham Stallonovich"},
    ]

    body = []
    for person in persons:
        body.append(json.dumps({"create": {"_index": "persons", "_id": person["id"]}}))
        body.append(json.dumps(person))

    await es_client.bulk(index="persons", body=body, refresh=True)
    yield
    await es_client.delete_by_query(
        index="persons", body={"query": {"match_all": {}}}, refresh=True
    )


@pytest.fixture(scope="session", autouse=True)
async def film_data(es_client):
    films = [
        {
            "id": "0550ff1f-4367-4b73-a29a-be69eb46070e",
            "title": "Star Wars: Episode V - The Empire Strikes Back",
            "imdb_rating": 8.7,
            "description": "description",
            "genres": [{"id": "c50ca5cb-f9bf-4845-aea0-a89a74bac72c", "name": "Fantasy"}],
            "actors": [
                {"id": "82ea4033-1ed9-4639-a52e-6454b3249a3a", "full_name": "Mark Hamill"},
                {"id": "facfb08d-8d9a-42f3-9e4e-697d8f9d6e4a", "full_name": "Harrison Ford"},
            ],
            "writers": [
                {"id": "b6ddf2ec-de20-4bb9-933b-5674edf70c1b", "full_name": "George Lucas"},
            ],
            "directors": [
                {"id": "b6ddf2ec-de20-4bb9-933b-5674edf70c1b", "full_name": "George Lucas"},
            ],
        },
        {
            "id": "e347570c-a59e-47ca-bc27-055319311541",
            "title": "Star Wars: Episode VI - Return of the Jedi",
            "imdb_rating": 8.3,
            "description": "description",
            "genres": [{"id": "c50ca5cb-f9bf-4845-aea0-a89a74bac72c", "name": "Fantasy"}],
            "actors": [
                {"id": "facfb08d-8d9a-42f3-9e4e-697d8f9d6e4a", "full_name": "Harrison Ford"}
            ],
            "writers": [
                {"id": "b6ddf2ec-de20-4bb9-933b-5674edf70c1b", "full_name": "George Lucas"},
                {"id": "facfb08d-8d9a-42f3-9e4e-697d8f9d6e4a", "full_name": "Harrison Ford"},
            ],
            "directors": [
                {"id": "82ea4033-1ed9-4639-a52e-6454b3249a3a", "full_name": "Mark Hamill"},
                {"id": "facfb08d-8d9a-42f3-9e4e-697d8f9d6e4a", "full_name": "Harrison Ford"},
            ],
        },
    ]

    body = []
    for film in films:
        body.append(json.dumps({"create": {"_index": "movies", "_id": film["id"]}}))
        body.append(json.dumps(film))

    await es_client.bulk(index="movies", body=body, refresh=True)
    yield
    await es_client.delete_by_query(index="movies", body={"query": {"match_all": {}}}, refresh=True)


@pytest.mark.parametrize(
    "method, expected_status_code",
    [
        ("/facfb08d-8d9a-42f3-9e4e-697d8f9d6e4a/", 200),
        ("/facfb08d-8d9a-42f3-9e4e-697d8f9d6e4a/film/", 200),
        ("invalid_method/", 404),
    ],
)
@pytest.mark.asyncio
async def test_person_status_code(make_person_request, method: str, expected_status_code: int):
    """Тест валидности выдаваемых status code"""
    response = await make_person_request(method=method)
    assert response.status == expected_status_code


@pytest.mark.parametrize(
    "person_id, expected_status_code, expected_body",
    [
        (
            "facfb08d-8d9a-42f3-9e4e-697d8f9d6e4a",
            200,
            {
                "id": "facfb08d-8d9a-42f3-9e4e-697d8f9d6e4a",
                "full_name": "Harrison Ford",
                "roles": ["actor", "director", "writer"],
                "film_ids": [
                    "0550ff1f-4367-4b73-a29a-be69eb46070e",
                    "e347570c-a59e-47ca-bc27-055319311541",
                ],
            },
        ),
        (
            "b6ddf2ec-de20-4bb9-933b-5674edf70c1b",
            200,
            {
                "id": "b6ddf2ec-de20-4bb9-933b-5674edf70c1b",
                "full_name": "George Lucas",
                "roles": ["director", "writer"],
                "film_ids": [
                    "0550ff1f-4367-4b73-a29a-be69eb46070e",
                    "e347570c-a59e-47ca-bc27-055319311541",
                ],
            },
        ),
        (
            "82ea4033-1ed9-4639-a52e-6454b3249a3a",
            200,
            {
                "id": "82ea4033-1ed9-4639-a52e-6454b3249a3a",
                "full_name": "Mark Hamill",
                "roles": ["actor", "director"],
                "film_ids": [
                    "0550ff1f-4367-4b73-a29a-be69eb46070e",
                    "e347570c-a59e-47ca-bc27-055319311541",
                ],
            },
        ),
        (
            "dfdbfd96-80ec-47fb-8c12-0b33db66baf5",
            200,
            {
                "id": "dfdbfd96-80ec-47fb-8c12-0b33db66baf5",
                "full_name": "Arnold Statham Stallonovich",
                "roles": [],
                "film_ids": [],
            },
        ),
        ("12345678-1234-1234-1234-123456789012", 404, {"detail": "person not found"}),
    ],
)
@pytest.mark.asyncio
async def test_person_detail(
    make_person_request, person_id: str, expected_status_code: int, expected_body: Dict
):
    """Тест детальной информации о персоне"""
    response = await make_person_request(method=f"/{person_id}/")
    assert response.status == expected_status_code
    assert response.headers["Content-Type"] == "application/json"
    assert response.body == expected_body


@pytest.mark.parametrize(
    "person_id, expected_status_code, expected_body",
    [
        (
            "facfb08d-8d9a-42f3-9e4e-697d8f9d6e4a",
            200,
            [
                {
                    "id": "0550ff1f-4367-4b73-a29a-be69eb46070e",
                    "title": "Star Wars: Episode V - The Empire Strikes Back",
                    "imdb_rating": 8.7,
                    "roles": ["actor"],
                },
                {
                    "id": "e347570c-a59e-47ca-bc27-055319311541",
                    "title": "Star Wars: Episode VI - Return of the Jedi",
                    "imdb_rating": 8.3,
                    "roles": ["actor", "director", "writer"],
                },
            ],
        ),
        (
            "b6ddf2ec-de20-4bb9-933b-5674edf70c1b",
            200,
            [
                {
                    "id": "0550ff1f-4367-4b73-a29a-be69eb46070e",
                    "title": "Star Wars: Episode V - The Empire Strikes Back",
                    "imdb_rating": 8.7,
                    "roles": ["director", "writer"],
                },
                {
                    "id": "e347570c-a59e-47ca-bc27-055319311541",
                    "title": "Star Wars: Episode VI - Return of the Jedi",
                    "imdb_rating": 8.3,
                    "roles": ["writer"],
                },
            ],
        ),
        (
            "82ea4033-1ed9-4639-a52e-6454b3249a3a",
            200,
            [
                {
                    "id": "0550ff1f-4367-4b73-a29a-be69eb46070e",
                    "title": "Star Wars: Episode V - The Empire Strikes Back",
                    "imdb_rating": 8.7,
                    "roles": ["actor"],
                },
                {
                    "id": "e347570c-a59e-47ca-bc27-055319311541",
                    "title": "Star Wars: Episode VI - Return of the Jedi",
                    "imdb_rating": 8.3,
                    "roles": ["director"],
                },
            ],
        ),
        ("dfdbfd96-80ec-47fb-8c12-0b33db66baf5", 200, []),
        ("12345678-1234-1234-1234-123456789012", 200, []),
    ],
)
@pytest.mark.asyncio
async def test_person_film_list(
    make_person_request, person_id: str, expected_status_code: int, expected_body: List
):
    """Тест фильмов в которых принимала участие персона"""
    response = await make_person_request(method=f"/{person_id}/film/")
    assert response.status == expected_status_code
    assert response.headers["Content-Type"] == "application/json"
    assert response.body == expected_body
