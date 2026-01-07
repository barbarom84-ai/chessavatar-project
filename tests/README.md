# ChessAvatar Tests

Comprehensive test suite for ChessAvatar application.

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_game.py
```

### Run with coverage
```bash
pytest --cov=core --cov=ui --cov-report=html
```

### Run UI tests only
```bash
pytest -m ui
```

### Run unit tests only
```bash
pytest -m unit
```

### Run excluding slow tests
```bash
pytest -m "not slow"
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- `test_game.py` - Chess game logic
- `test_pgn_manager.py` - PGN import/export
- `test_api_service.py` - API calls (mocked)
- `test_style_analyzer.py` - Style analysis
- `test_avatar_manager.py` - Avatar management

### UI Tests (`@pytest.mark.ui`)
- `ui/test_chessboard.py` - Chessboard widget

### Async Tests (`@pytest.mark.async`)
- Tests for engine_manager.py
- Tests for avatar_worker.py

### Integration Tests (`@pytest.mark.integration`)
- Full workflow tests
- Component interaction tests

### Slow Tests (`@pytest.mark.slow`)
- Performance tests
- Long-running operations

## Coverage

Current coverage goal: **80%+**

View coverage report:
```bash
pytest --cov=core --cov=ui --cov-report=html
# Open htmlcov/index.html in browser
```

## Continuous Integration

Tests run automatically on:
- Every push to `main` or `develop`
- Every pull request
- Multiple OS: Windows, Linux, macOS
- Multiple Python versions: 3.8 - 3.12

See `.github/workflows/ci.yml` for CI configuration.

## Writing New Tests

### Test Structure
```python
import pytest
from your_module import YourClass

@pytest.mark.unit
class TestYourClass:
    """Test YourClass"""
    
    def test_something(self):
        """Test something specific"""
        obj = YourClass()
        assert obj.method() == expected_value
```

### Using Fixtures
```python
def test_with_fixture(sample_pgn):
    """Use fixture from conftest.py"""
    assert "Test Game" in sample_pgn
```

### Mocking
```python
from unittest.mock import Mock, patch

@patch('requests.get')
def test_api_call(mock_get):
    """Mock external API call"""
    mock_get.return_value.json.return_value = {"data": "test"}
    # Your test code
```

## Troubleshooting

### Qt Platform Plugin Error
Set environment variable:
```bash
export QT_QPA_PLATFORM=offscreen  # Linux/macOS
set QT_QPA_PLATFORM=offscreen     # Windows
```

### Tests Hang
Some UI tests may need timeout:
```python
@pytest.mark.timeout(10)
def test_long_running():
    pass
```

### Import Errors
Ensure project root is in PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Test Dependencies

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

Main test packages:
- `pytest` - Testing framework
- `pytest-qt` - Qt testing support
- `pytest-asyncio` - Async testing
- `pytest-mock` - Mocking utilities
- `pytest-cov` - Coverage reporting

## Code Quality

### Format code
```bash
black core/ ui/ tests/
```

### Lint code
```bash
flake8 core/ ui/ tests/
```

### Type checking
```bash
mypy core/ ui/ --ignore-missing-imports
```

## Performance Testing

```bash
pytest --benchmark-only
```

## Test Metrics

- **Total Tests**: 100+
- **Coverage**: 80%+
- **Execution Time**: < 30 seconds
- **UI Tests**: 20+
- **Unit Tests**: 80+

## Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain 80%+ coverage
4. Add appropriate markers
5. Update this README if needed

## Resources

- [PyTest Documentation](https://docs.pytest.org/)
- [PyQt Testing](https://pytest-qt.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)

