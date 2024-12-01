# Command control server

- [Command control server](#command-control-server)
  - [Quickstart](#quickstart)
    - [1. Install dependecies with Poetry](#1-install-dependecies-with-poetry)
    - [3. Create `.env` file](#3-create-env-file)
    - [3. Setup database and migrations](#3-setup-database-and-migrations)
    - [4. Now you can run app](#4-now-you-can-run-app)
    - [5. Install pre-commit](#5-install-pre-commit)
    - [6. Running tests](#6-running-tests)
  - [Design](#design)
    - [Docs URL, CORS and Allowed Hosts](#docs-url-cors-and-allowed-hosts)

## Quickstart

### 1. Install dependecies with [Poetry](https://python-poetry.org/docs/)

```bash
# You can entry virtual environment with poetry 
poetry shell

# or run commands with `poetry run` prefix
poetry run <command>
```

```bash
poetry install
```

### 2. Create `.env` file

```bash
# Create copy of .env.example file
cp .env.example .env
```

### 3. Setup database and migrations

```bash
# Run database
docker compose up -d

# Run Alembic migrations
alembic upgrade head
```

### 4. Now you can run app

```bash
# Development mode
fastapi dev app/main.py
# Production mode
fastapi run app/main.py
```

### 5. Install pre-commit

[pre-commit](https://pre-commit.com/) is de facto standard now for pre push activities like isort or black or its nowadays replacement ruff.

```bash
# Install pre-commit
pre-commit install --install-hooks
```

### 6. Running tests

Note, it will create databases for session and run tests in many processes by default (using pytest-xdist) to speed up execution, based on how many CPU are available in environment.

For more details about initial database setup, see logic `app/tests/conftest.py` file, `fixture_setup_new_test_database` function.

Moreover, there is coverage pytest plugin with required code coverage level 100%.

```bash
# see all pytest configuration flags in pyproject.toml
pytest
```

## Design

### Docs URL, CORS and Allowed Hosts

There are some **opinionated** default settings in `/app/main.py` for documentation, CORS and allowed hosts.

1. Docs

    ```python
    app = FastAPI(
        title="minimal fastapi postgres template",
        version="6.0.0",
        description="https://github.com/rafsaf/minimal-fastapi-postgres-template",
        openapi_url="/openapi.json",
        docs_url="/",
    )
    ```

   Docs page is simpy `/` (by default in FastAPI it is `/docs`). You can change it completely for the project, just as title, version, etc.

2. CORS

    ```python
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in config.settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    ```

   If you are not sure what are CORS for, follow https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS. React and most frontend frameworks nowadays operate on `http://localhost:3000` thats why it's included in `BACKEND_CORS_ORIGINS` in .env file, before going production be sure to include your frontend domain here, like `https://my-fontend-app.example.com`.

3. Allowed Hosts

   ```python
   app.add_middleware(TrustedHostMiddleware, allowed_hosts=config.settings.ALLOWED_HOSTS)
   ```

   Prevents HTTP Host Headers attack, you shoud put here you server IP or (preferably) full domain under it's accessible like `example.com`. By default in .env there are two most popular records: `ALLOWED_HOSTS=["localhost", "127.0.0.1"]`
