#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> pytest"
poetry run pytest tests/ "$@"

echo "[OK] All tests passed."
