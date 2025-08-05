# Tests Directory

This directory contains all tests for the Verityn AI project.

## Test Structure

- `test_classification.py` - Tests for document classification functionality
- `test_chat_engine.py` - Tests for chat engine and multi-agent workflows
- `test_agents.py` - Tests for individual agents
- `test_retrieval.py` - Tests for retrieval and vector search functionality

## Running Tests

### Using pytest directly:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_classification.py

# Run with coverage
pytest --cov=backend --cov=frontend

# Run with verbose output
pytest -v
```

### Using UV:
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=backend --cov=frontend
```

## Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **Performance Tests**: Test system performance under load
- **RAGAS Tests**: Test chat response quality using RAGAS framework

## Test Data

Tests use synthetic data and mock responses to avoid external dependencies during testing. 