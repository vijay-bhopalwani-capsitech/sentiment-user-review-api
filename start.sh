#!/bin/bash

# Activate or create virtualenv
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate

# Upgrade pip & install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Restart FastAPI app using PM2
APP_NAME="fastapi-sentiment"
PORT=7005  # <--- change your desired port

# Kill if already running
pm2 delete $APP_NAME || true

# Start FastAPI with PM2
pm2 start uvicorn \
  --name "$APP_NAME" \
  --interpreter venv/bin/python \
  -- \
  main:app --host 0.0.0.0 --port $PORT

# Save PM2 process list
pm2 save
