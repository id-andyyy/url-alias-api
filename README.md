![Art](https://i.postimg.cc/XYf5YtLW/art.png)

![GitHub Created At](https://img.shields.io/github/created-at/id-andyyy/url-alias-api?style=flat&color=3C0081)
![](https://tokei.rs/b1/github/id-andyyy/url-alias-api?style=flat&category=code&color=3FDFFF)
![Top Language](https://img.shields.io/github/languages/top/id-andyyy/url-alias-api?style=flat)
![Pet Project](https://img.shields.io/badge/pet-project-8400FF)

# URL Alias Service

Cервис преобразования длинных URL в короткие уникальные URL, c возможностью просмотра статистики&nbsp;&#128279;.

## &#128268;&nbsp;API Endpoints

Реализованы следующие эндпоинты:

- &#129517;&nbsp;`GET /{short_id}/` - перейти по сокращённой ссылке. Каждый переход учитывается в статистике
- &#128279;&nbsp;`POST /api/links/` - создать короткую ссылку. Можно указать количество секунд, после которых ссылка станет недействительной. Требуется авторизация&nbsp;&#128274;
- &#128203;&nbsp;`GET /api/links/` - получить информацию о своих созданных ссылках. Можно отфильтровать неактивные ссылки и с истёкшим сроком действия. Доступна пагинация. Требуется авторизация&nbsp;&#128274;
- &#128202;&nbsp;`GET /api/stats/` - получить статистику по своим самым посещаемым ссылкам за последний час, последний день или за всё время. Можно настроить сортировку и количество отображаемых ссылок. Требуется авторизация&nbsp;&#128274;
- &#128200;&nbsp;`GET /api/stats/{short_id}/` - получить статистику по конкретной ссылке. Требуется авторизация&nbsp;&#128274;
- &#128161;&nbsp;`GET /health/` - проверка работоспособности сервиса

## &#128218;&nbsp;Технологии и инструменты

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffffff)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&color=009485&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%ff2f2e.svg?style=for-the-badge&logo=sqlalchemy&logoColor=white&color=ff2f2e)
![alembic](https://img.shields.io/badge/alembic-%230db7ed.svg?style=for-the-badge&logo=alembic&logoColor=white&color=black)
![Pytest](https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

- Python 3.11
- REST API на FastAPI
- PostgreSQL 13 на продакшен-стеке и в Docker Compose
- In-memory SQLite в тестах
- SQLAlchemy для работы с базой
- Alembic для миграций
- Базовая аутентификация (Basic Auth)
- Хранение паролей с bcrypt
- Pytest, TestClient и Monkeypatch для тестирования
- Docker и Docker compose

## &#128161;&nbsp;Принятые технические решения

- Валидация и схема данных
    - Pydantic v2 + pydantic-settings (описание входных/выходных JSON-моделей)
- ORM и работа с бд
    - SQLAlchemy (Declarative Base + `Mapped`/`mapped_column`)
- Миграции схемы
    - Alembic (предусмотрена возможность масштабирования бд без потери существующих данных)
    - В Docker при старте контейнера всегда выполняется `alembic upgrade head` для поддержки данных в актуальном состоянии
- Сокращение ссылок
    - Генерация случайных коротких идентификаторов (short_id) из букв и цифр
    - Проверка уникальности short_id перед сохранением
    - Настраиваемое время жизни ссылок (expire_seconds)
    - Отслеживание статистики переходов по ссылкам
- Аутентификация
    - Базовая аутентификация (Basic Auth)
    - Безопасное хранение паролей с использованием bcrypt (через passlib)
    - Скрипты для ручного создания пользователей (create_user.py)
    - Автоматическое создание дефолтного пользователя при запуске сервиса
- Контейнеризация
    - Docker Compose
        - Сервис `db` (Postgres 13 + volume для персистентности)
        - Сервис `web` (Healthcheck `pg_isready`, зависимость `depends_on: condition: service_healthy`)
    - Скрипт `entrypoint.sh` для автоматического запуска миграций, создания пользователя и запуска приложения
    - `.env` файл (стандартные переменные `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` для совместимости с Docker-образом Postgres и `DEFAULT_USER_USERNAME` и `DEFAULT_USER_PASSWORD` для автоматического создания пользователя на старте)
- Тестирование
    - Покрытие тестами >98% кода
    - TestClient (для end-to-end API-тестов без поднятия внешнего сервера)
    - In-memory SQLite (лёгкая изолированная бд для ускорения тестов)
    - Фикстуры с откатом транзакций (каждая `db_session` откатывает изменения после теста, сохраняя чистоту состояния)
- Обработка ошибок
    - Явные проверки входных данных
    - Глобальный `exception_handler` для IntegrityError
- Разделение слоёв
    - `routers/` - HTTP + валидация
    - `crud/` - операции с бд
    - `utils/` - утилитарные функции

## &#9997;&nbsp;Модели данных

- User&nbsp;&#128104;&#8205;&#128187; - модель пользователя с хешированными паролями
- Link&nbsp;&#128279; - модель для хранения оригинальных и коротких URL
- Click&nbsp;&#128070; - модель для регистрации переходов по ссылкам и сбора статистики

## &#128640;&nbsp;Как запустить сервис

1. Склонируйте репозиторий и перейдите в папку с проектом:
    ```bash
    git clone https://github.com/id-andyyy/url-alias-api.git
    cd url-alias-api
    ```

2. Создайте файл окружения на основе `.env.example`:
    ```bash
    cp .env.example .env
    ```

3. Если необходимо, заполните переменные `DEFAULT_USER_USERNAME` и `DEFAULT_USER_USERNAME` в файле `.env` чтобы при запуске сервера автоматически создавался пользователь. По умолчанию создается пользователь `admin` с паролем `admin`.

3. Запустите Docker Compose (не забудьте предварительно запустить Docker daemon):
    ```bash
    docker-compose up --build
    ```
    Дождитесь окончания процесса.

4. Проверьте работоспособность через терминал:
    ```bash
    curl http://0.0.0.0:8080/api/health
    ```
    
    Предполагаемый ответ:

    ```bash
    {"status":"ok"}
    ```

    Или через Swagger UI в браузере:

    ```bash
    http://127.0.0.1:8080/docs
    ```

5. Если хотите создать ещё одного пользователя:
    
    1. Перейдите в консоль:
        ```bash
        docker-compose exec web sh
        ```
    
    2. В консоли выполните команду (замените `new_user` и `secret_password` на желаемые значения):
        ```bash
        python3 create_user.py -u new_user -p secret_password
        ```
    
    3. Если создание пользователя прошло успешно, после сообщения о несовместимости версий (его можно проигнорировать), вы получите сообщение:
        ```bash
        New user created: username='new_user', id=2
        ```

    4. Для выхода из консоли выполните:
        ```bash
        exit
        ```

## 	&#129514;&nbsp;Как запустить тесты

1. Создайте и активируйте виртуальное окружение:
    ```bash
    python3 -m venv .venv

    source .venv/bin/activate       # На macOS / Linux
    .\.venv\Scripts\Activate.ps1    # На Windows
    ```

2. Установите зависимости
    ```bash
    pip install -r requirements.txt
    ```

3. Запустите тесты командой:
    ```bash
    pytest
    ```

## &#128221;&nbsp;Структура проекта

```
alembic/
│   ├── versions/       # Скрипты миграций
│   └── env.py          # Конфигурация Alembic

app/
├── api/
│   ├── routes/         # Эндпоинты и их логика
│   └── deps.py         # Зависимости FastAPI
├── core/
│   ├── config.py       # Чтение .env
├── crud/               # Функции работы с бд
├── db/
│   ├── base.py         # Базовый класс для DeclarativeBase
│   └── session.py      # Настройка engine и SessionLocal
├── models/             # Декларативные модели 
├── schemas/            # Модели запросов и ответов
├── utils/              # Утилитарные функции        
└── main.py             # Создание приложения

tests/
├── api/                # API-тесты через TestClient
├── crud/               # Unit-тесты CRUD-функций
├── fixtures/           # Дополнительные фикстуры
├── utils/              # Unit-тесты утилитарных функций
└── conftest.py         # Общие фикстуры       

.dockerignore           # Файлы, игнорируемые Docker
.env                    # Локальные переменные окружения
.env.example            # Пример содержимого .env
.gitignore              # Файлы, игнорируемые Git
alembic.ini             # Конфигурация Alembic
create_default_user.py  # Скрипт для автоматического создания пользователя при старте
create_user.py          # Скрипт для ручного создания пользователя
docker-compose.yaml     # Описание сервисов Docker
Dockerfile              # Инструкция сборки Docker-образа
entrypoint.sh           # Скрипт запуска контейнера web
requirements.txt        # Список зависимостей
```

## &#128232;&nbsp;Обратная связь

Буду признателен, если вы поставите звезду&nbsp;&#11088;. Если вы нашли баг или у вас есть предложения по улучшению, используйте раздел [Issues](https://github.com/id-andyyy/url-alias-api/issues).

Read in [English&nbsp;&#127468;&#127463;](README-en.md)