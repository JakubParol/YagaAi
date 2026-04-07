#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

if [[ "${1:-}" == "--fix" ]]; then
    echo "==> ruff check --fix"
    poetry run ruff check --fix .
    echo "==> ruff format"
    poetry run ruff format .
else
    echo "==> ruff check"
    poetry run ruff check .
    echo "==> ruff format --check"
    poetry run ruff format --check .
fi

echo "==> lint-imports"
poetry run lint-imports

echo "[OK] All lint checks passed."
