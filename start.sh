#!/bin/bash

# Start gateway in background
cd /app/gateway
sh bin/run.sh root/conf.yaml &

# Wait for gateway to start
sleep 5

# Start Flask
cd /app/webapp
export IBKR_ACCOUNT_ID="${IBKR_ACCOUNT_ID}"
PORT="${PORT:-5056}"
./venv/bin/python -m flask --app app run --host 0.0.0.0 --port $PORT
