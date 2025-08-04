#!/bin/bash

# --- Configuration ---
APP_NAME_API="fastapi-sentiment"
APP_NAME_WORKER="fastapi-worker"
PORT=8010
PYTHON=python3.12
PM2_PATH="/var/lib/jenkins/.nvm/versions/node/v18.20.8/bin/pm2"
UVICORN_BIN="/var/lib/jenkins/.local/bin/uvicorn"

# --- Install Python dependencies ---
$PYTHON -m pip install --upgrade pip --break-system-packages
$PYTHON -m pip install --break-system-packages -r requirements.txt

# --- Start FastAPI app ---
$PM2_PATH delete $APP_NAME_API || true
$PM2_PATH start $UVICORN_BIN \
  --name "$APP_NAME_API" \
  --interpreter $PYTHON \
  -- \
  app:app --host 0.0.0.0 --port $PORT

# --- Start Worker script (consumer) ---
$PM2_PATH delete $APP_NAME_WORKER || true
$PM2_PATH start worker.py \
  --name "$APP_NAME_WORKER" \
  --interpreter $PYTHON

# --- Save PM2 process list ---
$PM2_PATH save
