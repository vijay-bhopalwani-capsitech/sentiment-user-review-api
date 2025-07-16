#!/bin/bash
APP_NAME="fastapi-sentiment"
PORT=8010

PYTHON=python3.12
VENV_PATH="venv"
PM2_PATH="/var/lib/jenkins/.nvm/versions/node/v18.20.8/bin/pm2"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
  $PYTHON -m venv $VENV_PATH
fi

# Activate the virtual environment
source $VENV_PATH/bin/activate

# Upgrade pip and install requirements (override if needed)
pip install --upgrade pip
pip install --break-system-packages -r requirements.txt

# Delete old app if exists
$PM2_PATH delete $APP_NAME || true

# Start FastAPI using PM2 and uvicorn
$PM2_PATH start $VENV_PATH/bin/uvicorn \
  --name "$APP_NAME" \
  --interpreter $VENV_PATH/bin/python \
  -- \
  app:app --host 0.0.0.0 --port $PORT

# Save PM2 process list
$PM2_PATH save