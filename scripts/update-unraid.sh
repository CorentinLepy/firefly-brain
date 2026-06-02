#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/mnt/user/appdata/firefly-brain"
BACKEND_ENV_BACKUP="/mnt/user/appdata/firefly-brain-backend.env.backup"
ROOT_ENV_BACKUP="/mnt/user/appdata/firefly-brain-root.env.backup"

cd "$APP_DIR"

if [ -f backend/.env ]; then
  cp backend/.env "$BACKEND_ENV_BACKUP"
fi

if [ -f .env ]; then
  cp .env "$ROOT_ENV_BACKUP"
fi

git fetch origin
git reset --hard origin/main

if [ -f "$BACKEND_ENV_BACKUP" ]; then
  cp "$BACKEND_ENV_BACKUP" backend/.env
fi

if [ -f "$ROOT_ENV_BACKUP" ]; then
  cp "$ROOT_ENV_BACKUP" .env
elif [ -f .env.example ]; then
  cp .env.example .env
fi

docker compose up -d --build

echo "Firefly Brain updated."
