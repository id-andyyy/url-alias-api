#!/usr/bin/env bash
set -e

alembic upgrade head

python3 create_default_user.py

exec uvicorn app.main:app --host 0.0.0.0 --port 8080