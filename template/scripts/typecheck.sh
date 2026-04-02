#!/usr/bin/env bash
set -euo pipefail

echo "Running mypy type checker..."
mypy app
