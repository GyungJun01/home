# pysec - Python Security Scanner MVP

Python Security Scanner MVP with Bandit SAST integration.

## SPEC-SECURITY-001 Implementation

This is the MVP implementation of Python security scanner following SPEC-First TDD methodology.

## Features

- SAST scanning with Bandit integration
- CLI interface with Typer
- JSON and Rich text output
- Severity filtering (HIGH/MEDIUM/LOW)
- OWASP Top 10 mapping

## Installation

```bash
uv sync --all-extras
```

## Usage

```bash
# Basic scan
pysec scan ./my_project

# JSON output
pysec scan ./my_project --format json

# Filter by severity
pysec scan ./my_project --severity HIGH

# Save to file
pysec scan ./my_project --format json --output report.json
```

## Development

```bash
# Run tests
uv run pytest

# Type checking
uv run mypy src/pysec

# Linting
uv run ruff check src/pysec

# Coverage
uv run pytest --cov=src/pysec --cov-report=term-missing
```

## TRUST 5 Principles

- **T**est-first: TDD with 85%+ coverage
- **R**eadable: Mypy strict, Ruff linting
- **U**nified: Pydantic data models
- **S**ecured: Input validation, safe subprocess
- **T**rackable: TAG chain traceability

## License

MIT
