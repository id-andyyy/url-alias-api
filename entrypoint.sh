#!/usr/bin/env bash
set -e

alembic upgrade head

python3 init_superuser.py

exec uvicorn app.main:app --host 0.0.0.0 --port 8080