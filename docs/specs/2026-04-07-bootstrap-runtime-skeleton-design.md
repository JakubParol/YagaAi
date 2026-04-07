# Bootstrap Runtime Skeleton & Toolchain — Design Spec

**Work item:** YAGA-24
**Date:** 2026-04-07
**Status:** Approved

## Goal

Create the minimal Python project layout, tooling, and bootstrap commands for the
runtime slice. This is Block A (A1 + A2) from `phase-1-task-breakdown-v1.md`.

## Directory Layout

```
pyproject.toml                      # root workspace — dev deps, tool config
packages/
  contracts/
    pyproject.toml                  # zero internal deps
    yaga_contracts/
      __init__.py
      py.typed
  persistence/
    pyproject.toml                  # depends on contracts
    yaga_persistence/
      __init__.py
      py.typed
  runtime_core/
    pyproject.toml                  # depends on contracts
    yaga_runtime_core/
      __init__.py
      py.typed
services/
  runtime/
    pyproject.toml                  # depends on runtime-core, persistence, contracts
    yaga_runtime/
      __init__.py
      py.typed
    alembic.ini
    alembic/
      env.py
      versions/                     # empty initially
tests/
  __init__.py
  conftest.py
  unit/
    __init__.py
  integration/
    __init__.py
scripts/
  lint.sh                           # quality gate script
  test.sh                           # test runner script
```

## Monorepo Strategy

Per-package `pyproject.toml` with root workspace orchestration.

### Dependency Graph (inward only)

```
contracts  (leaf — no internal deps)
    ↑
persistence       (contracts)
runtime_core      (contracts)
    ↑
services/runtime  (runtime-core, persistence, contracts)
```

## Tooling Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | ^3.12 | Runtime |
| Poetry | >=1.8 | Package management |
| Ruff | latest | Linting + formatting |
| pytest | latest | Test runner |
| pytest-asyncio | latest | Async test support |
| import-linter | latest | Import boundary enforcement |
| Alembic | latest | Database migrations |
| SQLAlchemy | ^2.0 | ORM (declared in persistence, used by runtime) |

## Configuration Details

### Ruff (root `pyproject.toml`)

- Target: Python 3.12
- Line length: 88
- Rule sets: E, F, W, I (isort), UP (pyupgrade), B (bugbear), SIM
- Format: ruff format (black-compatible)

### pytest (root `pyproject.toml`)

- Test paths: `tests/`
- asyncio_mode: auto
- Strict markers

### import-linter (root `pyproject.toml`)

Four contracts enforcing the dependency rule:

1. `contracts` — cannot import from persistence, runtime_core, or runtime
2. `persistence` — can import from contracts only (not runtime_core or runtime)
3. `runtime_core` — can import from contracts only (not persistence or runtime)
4. `runtime` — can import from contracts, persistence, runtime_core

### Alembic (`services/runtime/`)

- `alembic.ini` with SQLite default path
- `env.py` wired to SQLAlchemy metadata (empty initially)
- Migrations directory at `services/runtime/alembic/versions/`

## Scripts

### `scripts/lint.sh`

```bash
ruff check .
ruff format --check .
lint-imports
```

Exit non-zero on any failure. Supports `--fix` flag for auto-fix mode.

### `scripts/test.sh`

```bash
pytest tests/ "$@"
```

Passes through extra args to pytest.

## Bootstrap Commands

| Command | Purpose |
|---------|---------|
| `poetry install` | Install all packages + dev deps |
| `scripts/test.sh` | Run test suite |
| `cd services/runtime && alembic upgrade head` | Run migrations |

## Acceptance Criteria

1. `poetry install` succeeds from clean checkout
2. `scripts/test.sh` runs and passes (smoke test included)
3. `scripts/lint.sh` passes with zero warnings
4. `cd services/runtime && alembic upgrade head` runs on clean environment
5. `lint-imports` passes — boundary contracts enforced
6. All packages importable: `python -c "import yaga_contracts, yaga_persistence, yaga_runtime_core, yaga_runtime"`

## Navigation

- [AGENTS.md](../../AGENTS.md)
- [docs/INDEX.md](../INDEX.md)
