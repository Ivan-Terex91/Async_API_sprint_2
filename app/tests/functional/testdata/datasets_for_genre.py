dataset_for_genre_detail_test = [
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
    ("invalid_id/", 404, {"detail": "Not Found"}),
]

dataset_for_status_code_test = [
    ("/", {}, 200),
    ("invalid_method/", {}, 404),
    ("/", {"size": "size", "page": "page", "sort": "sort"}, 422),
]

dataset_for_size_test = [size for size in range(1, 27)]
dataset_for_page_number_test = [(page, size) for page in range(2, 5) for size in range(1, 8)]
dataset_for_sort_tests = ["id", "name"]
