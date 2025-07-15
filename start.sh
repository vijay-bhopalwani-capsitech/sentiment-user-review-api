#!/bin/bash

APP_NAME="fastapi-sentiment"
PORT=8010

PYTHON=python3.12  # or python3 if 3.12 is default
VENV_PATH="venv"

# Create virtual environment if not exists
if [ ! -d "$VENV_PATH" ]; then
  $PYTHON -m venv $VENV_PATH
fi

# Activate virtual environment
source $VENV_PATH/bin/activate

# Install dependencies (force override if needed)
pip install --upgrade pip

# PEP 668 workaround: allow pip to run in system Python
pip install --break-system-packages -r requirements.txt

# Restart the FastAPI app using PM2
pm2 delete $APP_NAME || true

pm2 start uvicorn \
  --name "$APP_NAME" \
  --interpreter $VENV_PATH/bin/python \
  -- \
  main:app --host 0.0.0.0 --port $PORT

pm2 save
