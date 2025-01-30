# Hotline Agent

A FastAPI application for hotline agent.

## Requirements

- Python 3.11+
- Poetry for dependency management

## Installation

```bash
# Install dependencies
poetry install
```

## Quick Start

```bash
# Install dependencies
make install

# Start the application
make start

# Stop the application
make stop

# Clean up cache files
make clean
```

The API will be available at:
- http://localhost:8000 - API root
- http://localhost:8000/docs - Interactive API documentation
- http://localhost:8000/redoc - Alternative API documentation

## Development

```bash
# Run tests
poetry run pytest
