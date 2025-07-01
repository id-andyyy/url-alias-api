![Art](https://i.postimg.cc/XYf5YtLW/art.png)

![GitHub Created At](https://img.shields.io/github/created-at/id-andyyy/url-alias-api?style=flat&color=3C0081)
![](https://tokei.rs/b1/github/id-andyyy/url-alias-api?style=flat&category=code&color=3FDFFF)
![Top Language](https://img.shields.io/github/languages/top/id-andyyy/url-alias-api?style=flat)
![Pet Project](https://img.shields.io/badge/pet-project-8400FF)

# URL Alias Service

A service for converting long URLs into short unique URLs, with the ability to view statistics&nbsp;&#128279;.

## &#128268;&nbsp;API Endpoints

The following endpoints are implemented:

- &#129517;&nbsp;`GET /{short_id}/` - redirect to the original URL using the short link. Each redirect is tracked in the statistics.
- &#128279;&nbsp;`POST /api/links/` - create a short link. You can specify the number of seconds after which the link will become invalid. Authorization required&nbsp;&#128274;.
- &#128203;&nbsp;`GET /api/links/` - get information about your created links. You can filter by inactive and expired links. Pagination is available. Authorization required&nbsp;&#128274;.
- &#128202;&nbsp;`GET /api/stats/` - get statistics on your most visited links in the last hour, last day, or all time. You can configure sorting and the number of links displayed. Authorization required&nbsp;&#128274;.
- &#128200;&nbsp;`GET /api/stats/{short_id}/` - get statistics for a specific link. Authorization required&nbsp;&#128274;.
- &#128161;&nbsp;`GET /health/` - service health check.

## &#128218;&nbsp;Technologies and Tools

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffffff)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&color=009485&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%ff2f2e.svg?style=for-the-badge&logo=sqlalchemy&logoColor=white&color=ff2f2e)
![alembic](https://img.shields.io/badge/alembic-%230db7ed.svg?style=for-the-badge&logo=alembic&logoColor=white&color=black)
![Pytest](https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

- Python 3.11
- REST API with FastAPI
- PostgreSQL 13 on the production stack and in Docker Compose
- In-memory SQLite for tests
- SQLAlchemy for database operations
- Alembic for migrations
- Basic Authentication
- Password hashing with bcrypt
- Pytest, TestClient, and Monkeypatch for testing
- Docker and Docker Compose

## &#128161;&nbsp;Technical Decisions

- Data Validation and Schema
    - Pydantic v2 + pydantic-settings (description of input/output JSON models)
- ORM and Database Operations
    - SQLAlchemy (Declarative Base + `Mapped`/`mapped_column`)
- Schema Migrations
    - Alembic (provides the ability to scale the database without losing existing data)
    - In Docker, `alembic upgrade head` is always executed on container startup to keep the data up to date
- Link Shortening
    - Generation of random short identifiers (short_id) from letters and numbers
    - Uniqueness check of short_id before saving
    - Configurable link lifetime (expire_seconds)
    - Tracking of link click statistics
- Authentication
    - Basic Authentication
    - Secure password storage using bcrypt (via passlib)
    - Scripts for manual user creation (create_user.py)
    - Automatic creation of a default user when the service starts
- Containerization
    - Docker Compose
        - `db` service (Postgres 13 + volume for persistence)
        - `web` service (Healthcheck `pg_isready`, `depends_on: condition: service_healthy` dependency)
    - `entrypoint.sh` script for automatic execution of migrations, user creation, and application launch
    - `.env` file (standard variables `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` for compatibility with the Postgres Docker image, and `DEFAULT_USER_USERNAME` and `DEFAULT_USER_PASSWORD` for automatic user creation at startup)
- Testing
    - >98% code coverage
    - TestClient (for end-to-end API tests without running an external server)
    - In-memory SQLite (a lightweight, isolated database to speed up tests)
    - Fixtures with transaction rollback (each `db_session` rolls back changes after the test, keeping the state clean)
- Error Handling
    - Explicit input data checks
    - Global `exception_handler` for IntegrityError
- Layer Separation
    - `routers/` - HTTP + validation
    - `crud/` - database operations
    - `utils/` - utility functions

## &#9997;&nbsp;Data Models

- User&nbsp;&#128104;&#8205;&#128187; - user model with hashed passwords
- Link&nbsp;&#128279; - model for storing original and short URLs
- Click&nbsp;&#128070; - model for registering link clicks and collecting statistics

## &#128640;&nbsp;How to run the service

1. Clone the repository and navigate to the project folder:
    ```bash
    git clone https://github.com/id-andyyy/url-alias-api.git
    cd url-alias-api
    ```

2. Create an environment file based on `.env.example`:
    ```bash
    cp .env.example .env
    ```

3. If necessary, fill in the `DEFAULT_USER_USERNAME` and `DEFAULT_USER_PASSWORD` variables in the `.env` file to automatically create a user when the server starts. By default, a user `admin` with the password `admin` is created.

4. Start Docker Compose (don't forget to start the Docker daemon first):
    ```bash
    docker-compose up --build
    ```
    Wait for the process to finish.

5. Check the service's health via the terminal:
    ```bash
    curl http://0.0.0.0:8080/api/health
    ```
    
    Expected response:

    ```bash
    {"status":"ok"}
    ```

    Or via the Swagger UI in your browser:

    ```bash
    http://127.0.0.1:8080/docs
    ```

6. To create another user:
    
    1. Go to the console:
        ```bash
        docker-compose exec web sh
        ```
    
    2. In the console, execute the command (replace `new_user` and `secret_password` with your desired values):
        ```bash
        python3 create_user.py -u new_user -p secret_password
        ```
    
    3. If the user is created successfully, after a message about version incompatibility (which can be ignored), you will receive a message:
        ```bash
        New user created: username='new_user', id=2
        ```

    4. To exit the console, execute:
        ```bash
        exit
        ```

## &#129514;&nbsp;How to run tests

1. Create and activate a virtual environment:
    ```bash
    python3 -m venv .venv

    source .venv/bin/activate       # On macOS / Linux
    .\.venv\Scripts\Activate.ps1    # On Windows
    ```

2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the tests with the command:
    ```bash
    pytest
    ```

## &#128221;&nbsp;Project Structure

```
alembic/
│   ├── versions/       # Migration scripts
│   └── env.py          # Alembic configuration

app/
├── api/
│   ├── routes/         # Endpoints and their logic
│   └── deps.py         # FastAPI dependencies
├── core/
│   ├── config.py       # Reading .env
├── crud/               # Database operation functions
├── db/
│   ├── base.py         # Base class for DeclarativeBase
│   └── session.py      # Engine and SessionLocal setup
├── models/             # Declarative models 
├── schemas/            # Request and response models
├── utils/              # Utility functions        
└── main.py             # Application creation

tests/
├── api/                # API tests via TestClient
├── crud/               # Unit tests for CRUD functions
├── fixtures/           # Additional fixtures
├── utils/              # Unit tests for utility functions
└── conftest.py         # Common fixtures       

.dockerignore           # Files ignored by Docker
.env                    # Local environment variables
.env.example            # Example .env content
.gitignore              # Files ignored by Git
alembic.ini             # Alembic configuration
create_default_user.py  # Script for automatic user creation at startup
create_user.py          # Script for manual user creation
docker-compose.yaml     # Docker services description
Dockerfile              # Docker image build instructions
entrypoint.sh           # web container startup script
requirements.txt        # List of dependencies
```

## &#128232;&nbsp;Feedback

I would appreciate it if you give it a star&nbsp;&#11088;. If you find a bug or have suggestions for improvement, please use the [Issues](https://github.com/id-andyyy/url-alias-api/issues) section.

Читать на [русском&nbsp;🇷🇺](README.md)