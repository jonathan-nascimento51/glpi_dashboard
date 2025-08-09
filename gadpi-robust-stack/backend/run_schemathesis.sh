#!/usr/bin/env bash
set -euo pipefail
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
PID=$!
sleep 2
schemathesis run http://127.0.0.1:8000/openapi.json --checks all --hypothesis-deadline=500
kill $PID