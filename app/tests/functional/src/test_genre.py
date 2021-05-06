from typing import Dict

import pytest

GENRE_FIELDS = ["id", "name"]


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
    make_genre_request, genre_id: str, expected_status_code: int, expected_body: Dict
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
