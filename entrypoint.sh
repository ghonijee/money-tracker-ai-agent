#!/usr/bin/env bash
alembic upgrade head

granian --port 8000 --interface asgi --host 0.0.0.0 src.main:app