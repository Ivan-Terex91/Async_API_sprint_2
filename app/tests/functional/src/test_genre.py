from typing import Dict

import pytest

from app.tests.functional.testdata.datasets_for_genre import (
    dataset_for_genre_detail_test,
    dataset_for_page_number_test,
    dataset_for_size_test,
    dataset_for_sort_tests,
    dataset_for_status_code_test,
)

GENRE_PREFIX = "/api/v1/genre"
GENRE_FIELDS = ["id", "name"]


@pytest.mark.parametrize(
    "genre_id, expected_status_code, expected_body", dataset_for_genre_detail_test
)
@pytest.mark.asyncio
async def test_genre_detail(
    make_get_request, genre_id: str, expected_status_code: int, expected_body: Dict
):
    """Тест детальной информации о жанре"""
    response = await make_get_request(prefix=GENRE_PREFIX, method=f"/{genre_id}/")
    assert response.status == expected_status_code
    assert response.headers["Content-Type"] == "application/json"
    assert response.body == expected_body


@pytest.mark.parametrize("method, params, expected_status_code", dataset_for_status_code_test)
@pytest.mark.asyncio
async def test_genre_list_status_code(
    make_get_request, method: str, params: Dict, expected_status_code: int
):
    """Тест валидности выдаваемых status code"""
    response = await make_get_request(prefix=GENRE_PREFIX, method=method, params=params)
    assert response.status == expected_status_code


@pytest.mark.asyncio
async def test_genre_list(make_get_request):
    """Тест списка жанров"""
    response = await make_get_request(prefix=GENRE_PREFIX, method="/")
    assert response.status == 200
    assert response.headers["Content-Type"] == "application/json"
    assert all(sorted(list(genre.keys())) == GENRE_FIELDS for genre in response.body)


@pytest.mark.parametrize("size", dataset_for_size_test)
@pytest.mark.asyncio
async def test_genre_list_page_size(make_get_request, size: int):
    """Тест размера ответа списка жанров"""
    response = await make_get_request(prefix=GENRE_PREFIX, method="/", params={"size": size})
    assert response.status == 200
    assert len(response.body) == size


@pytest.mark.parametrize("page, size", dataset_for_page_number_test)
@pytest.mark.asyncio
async def test_genre_list_page_number(make_get_request, page: int, size: int):
    """Тест номера страницы списка жанров"""
    all_genres = await make_get_request(prefix=GENRE_PREFIX, method="/")
    response = await make_get_request(
        prefix=GENRE_PREFIX, method="/", params={"size": size, "page": page}
    )
    assert response.status == 200
    assert all_genres.body[size * (page - 1) : (size * page)] == response.body


@pytest.mark.parametrize("sort_field", dataset_for_sort_tests)
@pytest.mark.asyncio
async def test_genre_list_sort_asc(make_get_request, sort_field: str):
    """Тест списка жанров c сортировкой по id и name в порядке возрастания"""
    response = await make_get_request(prefix=GENRE_PREFIX, method="/", params={"sort": sort_field})
    assert response.status == 200
    assert all(
        response.body[i][sort_field] < response.body[i + 1][sort_field]
        for i in range(len(response.body) - 1)
    )


@pytest.mark.parametrize("sort_field", dataset_for_sort_tests)
@pytest.mark.asyncio
async def test_genre_list_sort_desc(make_get_request, sort_field: str):
    """Тест списка жанров c сортировкой по id и name в порядке убывания"""
    response = await make_get_request(
        prefix=GENRE_PREFIX, method="/", params={"sort": f"-{sort_field}"}
    )
    assert response.status == 200
    assert all(
        response.body[i][sort_field] > response.body[i + 1][sort_field]
        for i in range(len(response.body) - 1)
    )
