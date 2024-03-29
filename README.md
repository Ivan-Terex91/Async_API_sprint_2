[Функциональны тесты. Инф-ра](https://github.com/smdnv/Async_API_sprint_2/pull/10)
1. Добавлено окружение для запуска тестов в докере и локально.
2. Добавлены фикстуры настроек тестов, клиентов redis, elastic, http

[Функциональны тесты. genre](https://github.com/smdnv/Async_API_sprint_2/pull/9)
1. Добавлены тесты для api жанров

[Функциональны тесты. film](https://github.com/smdnv/Async_API_sprint_2/pull/12)
1. Добавлены тесты для api фильмов

[Функциональны тесты. person](https://github.com/smdnv/Async_API_sprint_2/pull/11)
1. Добавлены тесты для api персон

[Функциональны тесты. search](https://github.com/smdnv/Async_API_sprint_2/pull/14)
1. Добавлены тесты для api поиска

[SOLID. Redis](https://github.com/smdnv/Async_API_sprint_2/pull/13)
1. Добавлен абстрактный класс хранилища для кеширования
2. Добавлена реализация хранилища с использованием редиса

[SOLID. Elastic](https://github.com/smdnv/Async_API_sprint_2/pull/15)
1. Добавлен абстрактный класс хранилища для общих данных
2. Добавлена реализация хранилища с использованием еластика для моделей фильмов, жанров и персонажей


# Запуск проекта
1. Конфигурация маппинга портов для локального запуска
```
cp docker-compose.override.yml{.example,}
```
2. Переменные окружения для запуска
```
cp .env{.example,}
```
3. Запуск контейнеров
```
docker-compose up -d
```

* В проекте находится тестовая бд, которая автоматически разворачивается в контейнере с postgres.
* Etl создаст нужные индексы в elastic и скопирует данные, после запуска elastic контейнера.
```
docker-compose logs -f --tail 30 etl
```
для просмотра процесса синхронизации данных.


# Запуск тестов
1. Переменные окружения для тестов
```
cd tests/functional
cp .env{.example,}  # Переменные окружения для запуска в докере
cp .local.env{.example,}  # Переменные окружения для запуска локально
```

2. Запуск всех тестов в докере
```
cd tests/functional
docker-compose up -d
docker-compose logs -f --tail 100 tests
```

3. Запуск тестов в докере
Для запуска тестов внутри докера нужно переопределить команду для запуска контейнера `tests`. Для это нужно скопировать пример `docker-compose.override`.
```
cd tests/functional
cp docker-compose.override.yml{.example,}
```
Пересоздать контейнер и запустить `pytest` внутри контейнера
```
docker-compose --force-recreate tests
docker-compose exec tests /bin/bash
pytest
```

4. Запуск тестов локально
Для запуска тестов локально должны быть подняты контейнеры `api, elastic, redis` и данные для подключения указаны в `.local.env`. При запуске тестов переменные считаются автоматически.
```
cd tests/functional
pytest
```

# Команда для дампа фикстур из elastic
``` sh
cat query.json
{
    "sort": [
        {
            "imdb_rating": {
                "order": "desc"
            }
        }
    ]
}

cat query.json | http get http://localhost:9200/movies/_search | jq '[.hits.hits[]._source]' > movies.json
```


# Проектная работа 5 спринта

В папке **tasks** ваша команда найдёт задачи, которые необходимо выполнить во втором спринте второго модуля.

Как и в прошлом спринте, мы оценили задачи в стори поинтах.

Вы можете разбить эти задачи на более маленькие, например, распределять между участниками команды не большие куски задания, а маленькие подзадачи. В таком случае не забудьте зафиксировать изменения в issues в репозитории.

**От каждого разработчика ожидается выполнение минимум 40% от общего числа стори поинтов в спринте.**
