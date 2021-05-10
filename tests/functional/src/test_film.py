import json
from functools import partial
from pathlib import Path
from typing import List

import pytest


@pytest.fixture(scope="session")
async def make_film_request(make_get_request):
    return partial(make_get_request, prefix="/api/v1/film")


@pytest.fixture(scope="module", autouse=True)
async def film_data(es_client):
    fixture_path = Path(".") / "testdata" / "movies.json"
    with fixture_path.open() as fixture_file:
        films = json.load(fixture_file)

    body = []
    for film in films:
        body.append(json.dumps({"create": {"_index": "movies", "_id": film["id"]}}))
        body.append(json.dumps(film))

    await es_client.bulk(index="movies", body=body, refresh=True)
    yield
    await es_client.delete_by_query(index="movies", body={"query": {"match_all": {}}}, refresh=True)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "film_id, expected_status_code, expected_body",
    [
        (
            "b05e03d9-3e7e-4233-ba9b-f81e417fc4b3",
            200,
            {
                "id": "b05e03d9-3e7e-4233-ba9b-f81e417fc4b3",
                "title": "Star Wars: Knights of the Old Republic",
                "description": "Four thousand years before the fall of the Republic, before the fall of the Jedi, a great war was fought, between the armies of the Sith and the forces of the Republic. A warrior is chosen to rescue a Jedi with a power important to the cause of the Republic, but in the end, will the warrior fight for the Light Side of the Force, or succumb to the Darkness?",
                "imdb_rating": 9.6,
                "genres": [
                    {"name": "Adventure", "id": "41062d8b-1f6d-4fc6-adf7-fc3412bafc47"},
                    {"name": "Action", "id": "a4d63486-7447-46df-98cc-55735180941a"},
                    {"name": "Fantasy", "id": "c50ca5cb-f9bf-4845-aea0-a89a74bac72c"},
                ],
                "directors": [
                    {"full_name": "Casey Hudson", "id": "39540ddc-dfcb-4604-b290-d48df04af668"}
                ],
                "writers": [
                    {"full_name": "Michael Gallo", "id": "1e010393-a089-4d23-9a42-c6880ff49488"},
                    {"full_name": "Lynn Taylor", "id": "54c1129c-4928-4330-8850-8c8ba2eebf3e"},
                    {
                        "full_name": "Lukas Kristjanson",
                        "id": "5fad0857-2002-4880-b116-1388de87d410",
                    },
                    {"full_name": "Drew Karpyshyn", "id": "68ea803e-708e-46b2-a8c8-e139553bea08"},
                    {"full_name": "Peter Thomas", "id": "8b8d1c0c-7772-44c4-adbd-f49c3a769ae0"},
                    {"full_name": "David Gaider", "id": "ab707394-9ea8-4920-800a-a8c6ddef8a65"},
                    {"full_name": "Brett Rector", "id": "af743702-3f8e-4365-95b9-56995dac927f"},
                    {"full_name": "James Ohlen", "id": "ff582f40-fd41-41fd-a60c-7b40bb9362ab"},
                ],
                "actors": [
                    {"full_name": "Jennifer Hale", "id": "3e56cf4f-58d1-4eb5-884c-4258e22dacab"},
                    {"full_name": "John Cygan", "id": "5482fc83-1a01-4019-8eb9-916ea25f0661"},
                    {"full_name": "Raphael Sbarge", "id": "a8bf24b4-f147-4f1b-8f8d-18776e526bac"},
                    {"full_name": "Rafael Ferrer", "id": "bd3f1391-c785-447e-a1a0-ceb14f7dd2e7"},
                ],
            },
        ),
        (
            "9c472cfa-7d31-4d6c-868f-274e8f40fa27",
            200,
            {
                "id": "9c472cfa-7d31-4d6c-868f-274e8f40fa27",
                "title": "The Secret World of Jeffree Star",
                "description": "Shane Dawson interviews and spends a day with one of the most interesting and controversial people on the internet, Jeffrey Star, in a five part series.",
                "imdb_rating": 9.5,
                "genres": [{"name": "Documentary", "id": "20703a29-1e6d-4b7e-9c10-b2d12a000820"}],
                "directors": [],
                "writers": [],
                "actors": [
                    {"full_name": "Shane Dawson", "id": "a993d3a9-543c-457e-9a8e-faec13014dbe"},
                    {"full_name": "Jeffree Star", "id": "86f6ae6b-a8ba-453b-9e9f-4a41d55e456e"},
                ],
            },
        ),
        ("219710f5-1d2c-4edc-855b-c98d675305b8", 404, {"detail": "film not found"}),
    ],
)
async def test_film_detail(
    film_id: str, expected_status_code: int, expected_body: dict, make_film_request
):
    response = await make_film_request(method=f"/{film_id}/")
    assert response.status == expected_status_code
    assert response.headers["Content-Type"] == "application/json"
    assert response.body == expected_body


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query_params, expected_body",
    [
        (
            {"page[size]": 3},
            [
                {
                    "id": "b05e03d9-3e7e-4233-ba9b-f81e417fc4b3",
                    "imdb_rating": 9.6,
                    "title": "Star Wars: Knights of the Old Republic",
                },
                {
                    "id": "9c472cfa-7d31-4d6c-868f-274e8f40fa27",
                    "imdb_rating": 9.5,
                    "title": "The Secret World of Jeffree Star",
                },
                {
                    "id": "4d469eef-1635-4f8d-9ec5-be85cc5c3c2d",
                    "imdb_rating": 9.5,
                    "title": "Star Wars SC 38 Reimagined",
                },
            ],
        ),
        (
            {"page[size]": 3, "page[number]": 2},
            [
                {
                    "id": "b7985b06-3f6f-4f95-8dbc-61a5efc8f02e",
                    "imdb_rating": 9.4,
                    "title": "Ringo Rocket Star and His Song for Yuri Gagarin",
                },
                {
                    "id": "407585a5-1cb0-4d02-b4f6-522bac38d852",
                    "imdb_rating": 9.2,
                    "title": "Kirby Super Star",
                },
                {
                    "id": "532aa198-cc1c-4469-af4d-e1bd899a6c2d",
                    "imdb_rating": 9.2,
                    "title": "Lunar: The Silver Star",
                },
            ],
        ),
        (
            {"page[size]": 3, "sort": "imdb_rating"},
            [
                {
                    "id": "dd3b5822-4ce8-4721-8c52-053828c88805",
                    "imdb_rating": 9.1,
                    "title": "Star Control 2",
                },
                {
                    "id": "9e498b00-e3df-42be-b262-f3e708371dac",
                    "imdb_rating": 9.1,
                    "title": "Double Digits: The Story of a Neighborhood Movie Star",
                },
                {
                    "id": "407585a5-1cb0-4d02-b4f6-522bac38d852",
                    "imdb_rating": 9.2,
                    "title": "Kirby Super Star",
                },
            ],
        ),
        (
            {"filter[genre]": "9ad58da7-a676-4d1c-961f-f833703f2a5a"},
            [
                {
                    "id": "9e498b00-e3df-42be-b262-f3e708371dac",
                    "imdb_rating": 9.1,
                    "title": "Double Digits: The Story of a Neighborhood Movie Star",
                },
            ],
        ),
    ],
)
async def test_film_list(query_params, expected_body, make_film_request):
    response = await make_film_request(method="/", params=query_params)
    assert response.status == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.body == expected_body


@pytest.mark.parametrize(
    "title, expected_status_code, expected_body",
    [
        (
            "Star",
            200,
            [
                {
                    "id": "407585a5-1cb0-4d02-b4f6-522bac38d852",
                    "title": "Kirby Super Star",
                    "imdb_rating": 9.2,
                },
                {
                    "id": "532aa198-cc1c-4469-af4d-e1bd899a6c2d",
                    "title": "Lunar: The Silver Star",
                    "imdb_rating": 9.2,
                },
                {
                    "id": "dd3b5822-4ce8-4721-8c52-053828c88805",
                    "title": "Star Control 2",
                    "imdb_rating": 9.1,
                },
                {
                    "id": "9c472cfa-7d31-4d6c-868f-274e8f40fa27",
                    "title": "The Secret World of Jeffree Star",
                    "imdb_rating": 9.5,
                },
                {
                    "id": "b05e03d9-3e7e-4233-ba9b-f81e417fc4b3",
                    "title": "Star Wars: Knights of the Old Republic",
                    "imdb_rating": 9.6,
                },
                {
                    "id": "4d469eef-1635-4f8d-9ec5-be85cc5c3c2d",
                    "title": "Star Wars SC 38 Reimagined",
                    "imdb_rating": 9.5,
                },
                {
                    "id": "eab9d4f4-c5e3-4e7c-9dc5-701405205b40",
                    "title": "Rifftrax: The Star Wars Holiday Special",
                    "imdb_rating": 9.2,
                },
                {
                    "id": "74e1324f-c444-43da-aefa-4ca4823bfd41",
                    "title": "All-Star Party for Carol Burnett",
                    "imdb_rating": 9.2,
                },
                {
                    "id": "9e498b00-e3df-42be-b262-f3e708371dac",
                    "title": "Double Digits: The Story of a Neighborhood Movie Star",
                    "imdb_rating": 9.1,
                },
                {
                    "id": "b7985b06-3f6f-4f95-8dbc-61a5efc8f02e",
                    "title": "Ringo Rocket Star and His Song for Yuri Gagarin",
                    "imdb_rating": 9.4,
                },
            ],
        ),
        ("Yandex-middle-Python", 200, []),
    ],
)
@pytest.mark.asyncio
async def test_search_film(
    make_film_request, title: str, expected_status_code: int, expected_body: List
):
    """Тест поиска фильмов по названию"""
    response = await make_film_request(method="/search/", params={"query": title})
    assert response.status == expected_status_code
    assert response.headers["Content-Type"] == "application/json"
    assert response.body == expected_body


@pytest.mark.parametrize("title, size", [("Star", size) for size in range(1, 9)])
@pytest.mark.asyncio
async def test_search_film_page_size(make_film_request, title: str, size: int):
    """Тест размера ответа поиска фильмов"""
    response = await make_film_request(method="/search/", params={"query": title, "size": size})
    assert response.status == 200
    assert len(response.body) == size


@pytest.mark.parametrize(
    "title, page, size",
    [("Star", page, size) for page in range(2, 4) for size in range(1, 5)],
)
@pytest.mark.asyncio
async def test_search_film_page_number(make_film_request, title: str, page: int, size: int):
    """Тест номера страницы поиска фильмов"""
    all_films_search = await make_film_request(method="/search/", params={"query": title})
    response = await make_film_request(
        method="/search/", params={"query": title, "size": size, "page": page}
    )
    assert response.status == 200
    assert all_films_search.body[size * (page - 1) : (size * page)] == response.body
