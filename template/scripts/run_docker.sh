#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="fastapi-template"

echo "Building Docker image: $IMAGE_NAME"
docker build -t "$IMAGE_NAME" .

echo "Running Docker container on port 8000..."
docker run --rm -p 8000:8000 --env-file .env "$IMAGE_NAME"
