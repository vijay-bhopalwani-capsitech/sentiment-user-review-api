#!/bin/bash

APP_NAME="fastapi-sentiment"
PORT=8010
PYTHON=python3.12
PM2_PATH="/var/lib/jenkins/.nvm/versions/node/v18.20.8/bin/pm2"
UVICORN_BIN="/var/lib/jenkins/.local/bin/uvicorn"

# Install dependencies at user level (avoiding PEP 668)
$PYTHON -m pip install --upgrade pip --break-system-packages
$PYTHON -m pip install --break-system-packages -r requirements.txt

# Delete existing app if running
$PM2_PATH delete $APP_NAME || true

# Start FastAPI using PM2 with system Python
$PM2_PATH start $UVICORN_BIN \
  --name "$APP_NAME" \
  --interpreter $PYTHON \
  -- \
  app:app --host 0.0.0.0 --port $PORT

# Save PM2 process list
$PM2_PATH save
