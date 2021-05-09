import json
from functools import partial
from typing import Dict

import pytest

GENRE_FIELDS = ["id", "name"]
GENRE_PREFIX = "/api/v1/genre"


@pytest.fixture(scope="session")
async def make_genre_request(make_get_request):
    return partial(make_get_request, prefix=GENRE_PREFIX)


@pytest.fixture(scope="session", autouse=True)
async def genre_data(es_client):
    genres = [
        {"id": "a4d63486-7447-46df-98cc-55735180941a", "name": "Action", "description": ""},
        {"id": "41062d8b-1f6d-4fc6-adf7-fc3412bafc47", "name": "Adventure", "description": ""},
        {"id": "f1b24268-81cd-49b5-8e6c-51ef463593d3", "name": "Animation", "description": ""},
        {"id": "9ad58da7-a676-4d1c-961f-f833703f2a5a", "name": "Biography", "description": ""},
        {"id": "beaefac6-caf8-4a40-9665-7e1a946775ee", "name": "Comedy", "description": ""},
        {"id": "4e0b3cac-4839-44a3-a0d2-f5febf5e5207", "name": "Crime", "description": ""},
        {"id": "20703a29-1e6d-4b7e-9c10-b2d12a000820", "name": "Documentary", "description": ""},
        {"id": "4348c960-ebdd-4c1a-8fa9-c70f9503e619", "name": "Drama", "description": ""},
        {"id": "977819e5-de69-415e-91a9-554e42d23f3f", "name": "Family", "description": ""},
        {"id": "c50ca5cb-f9bf-4845-aea0-a89a74bac72c", "name": "Fantasy", "description": ""},
        {"id": "24dba79d-cca5-4496-ba25-67de5f2ca3fa", "name": "Game-Show", "description": ""},
        {"id": "93692d21-7943-46cf-95e6-306621566e2d", "name": "History", "description": ""},
        {"id": "676aecd4-caf8-485a-95fa-30797a1e3b45", "name": "Horror", "description": ""},
        {"id": "0ce6a59c-56d0-4990-a9b9-5eeae67e5667", "name": "Music", "description": ""},
        {"id": "ac31ed95-054c-476e-a726-59de23d24459", "name": "Musical", "description": ""},
        {"id": "11d149ef-2724-49bf-85ec-6c2d2b0c6aab", "name": "Mystery", "description": ""},
        {"id": "6d1e3e70-5527-41cd-9b36-ccc42b862130", "name": "News", "description": ""},
        {"id": "b2630044-f57e-4664-a857-1c5cb145e9bb", "name": "Reality-TV", "description": ""},
        {"id": "d33072b8-d7d5-41b7-bda1-a102f6c1f796", "name": "Romance", "description": ""},
        {"id": "373e70ea-d61c-4041-ad73-c041c68d8d84", "name": "Sci-Fi", "description": ""},
        {"id": "d781c246-c087-49a7-8af1-1affa33a13f7", "name": "Short", "description": ""},
        {"id": "9aea9fe8-ed6e-4ac9-b25d-f60366ef5ffb", "name": "Sport", "description": ""},
        {"id": "5a892959-e8c3-4af0-b5fb-38aab3c16b35", "name": "Talk-Show", "description": ""},
        {"id": "1fd215f8-6d65-4169-99e5-361b7afb8e21", "name": "Thriller", "description": ""},
        {"id": "54af7cfa-8fcf-4cdb-a81e-1fb69158af8c", "name": "War", "description": ""},
        {"id": "fce8653d-f492-41a5-87d3-37b3154b0c0c", "name": "Western", "description": ""},
    ]
    body = []
    for genre in genres:
        body.append(json.dumps({"create": {"_index": "genres", "_id": genre["id"]}}))
        body.append(json.dumps(genre))

    await es_client.bulk(index="genres", body=body, refresh="wait_for")


@pytest.mark.parametrize(
    "genre_id, expected_status_code, expected_body",
    [
        (
            "a4d63486-7447-46df-98cc-55735180941a",
            200,
            {"id": "a4d63486-7447-46df-98cc-55735180941a", "name": "Action"},
        ),
        (
            "4e0b3cac-4839-44a3-a0d2-f5febf5e5207",
            200,
            {"id": "4e0b3cac-4839-44a3-a0d2-f5febf5e5207", "name": "Crime"},
        ),
        (
            "676aecd4-caf8-485a-95fa-30797a1e3b45",
            200,
            {"id": "676aecd4-caf8-485a-95fa-30797a1e3b45", "name": "Horror"},
        ),
        (
            "9aea9fe8-ed6e-4ac9-b25d-f60366ef5ffb",
            200,
            {"id": "9aea9fe8-ed6e-4ac9-b25d-f60366ef5ffb", "name": "Sport"},
        ),
        (
            "54af7cfa-8fcf-4cdb-a81e-1fb69158af8c",
            200,
            {"id": "54af7cfa-8fcf-4cdb-a81e-1fb69158af8c", "name": "War"},
        ),
        ("invalid_id", 404, {"detail": "Not Found"}),
    ],
)
@pytest.mark.asyncio
async def test_genre_detail(
    make_genre_request,
    genre_id: str,
    expected_status_code: int,
    expected_body: Dict,
):
    """Тест детальной информации о жанре"""
    response = await make_genre_request(method=f"/{genre_id}/")

    assert response.status == expected_status_code
    assert response.headers["Content-Type"] == "application/json"
    assert response.body == expected_body


@pytest.mark.parametrize(
    "method, params, expected_status_code",
    [
        ("/", {}, 200),
        ("invalid_method/", {}, 404),
        ("/", {"size": "size", "page": "page", "sort": "sort"}, 422),
    ],
)
@pytest.mark.asyncio
async def test_genre_list_status_code(
    make_genre_request, method: str, params: Dict, expected_status_code: int
):
    """Тест валидности выдаваемых status code"""
    response = await make_genre_request(method=method, params=params)
    assert response.status == expected_status_code


@pytest.mark.asyncio
async def test_genre_list(make_genre_request):
    """Тест списка жанров"""
    response = await make_genre_request(method="/")

    assert response.status == 200
    assert response.headers["Content-Type"] == "application/json"
    assert all(sorted(list(genre.keys())) == GENRE_FIELDS for genre in response.body)


@pytest.mark.parametrize("size", [size for size in range(1, 27)])
@pytest.mark.asyncio
async def test_genre_list_page_size(make_genre_request, size: int):
    """Тест размера ответа списка жанров"""
    response = await make_genre_request(method="/", params={"size": size})
    assert response.status == 200
    assert len(response.body) == size


@pytest.mark.parametrize(
    "page, size", [(page, size) for page in range(2, 5) for size in range(1, 8)]
)
@pytest.mark.asyncio
async def test_genre_list_page_number(make_genre_request, page: int, size: int):
    """Тест номера страницы списка жанров"""
    all_genres = await make_genre_request(method="/")
    response = await make_genre_request(method="/", params={"size": size, "page": page})
    assert response.status == 200
    assert all_genres.body[size * (page - 1) : (size * page)] == response.body


@pytest.mark.parametrize("sort_field", ["id", "name"])
@pytest.mark.asyncio
async def test_genre_list_sort_asc(make_genre_request, sort_field: str):
    """Тест списка жанров c сортировкой по id и name в порядке возрастания"""
    response = await make_genre_request(method="/", params={"sort": sort_field})
    assert response.status == 200
    assert all(
        response.body[i][sort_field] < response.body[i + 1][sort_field]
        for i in range(len(response.body) - 1)
    )


@pytest.mark.parametrize("sort_field", ["id", "name"])
@pytest.mark.asyncio
async def test_genre_list_sort_desc(make_genre_request, sort_field: str):
    """Тест списка жанров c сортировкой по id и name в порядке убывания"""
    response = await make_genre_request(method="/", params={"sort": f"-{sort_field}"})
    assert response.status == 200
    assert all(
        response.body[i][sort_field] > response.body[i + 1][sort_field]
        for i in range(len(response.body) - 1)
    )
