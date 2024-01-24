#!/bin/ash

echo "test"

uvicorn mmisp.worker.main:app --reload
echo "test"

exec "$@"