#!/usr/bin/env bash
set -euo pipefail

echo "Running Black formatter..."
black .
echo "Running Ruff format check and fix..."
ruff check --fix .
