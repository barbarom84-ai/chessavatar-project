"""
PyTest Configuration and Fixtures
Shared fixtures for all tests
"""
import pytest
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for all UI tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def sample_pgn():
    """Sample PGN for testing"""
    return """[Event "Test Game"]
[Site "Test"]
[Date "2024.01.01"]
[Round "1"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 1-0
"""


@pytest.fixture
def sample_fen():
    """Sample FEN position for testing"""
    return "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


@pytest.fixture
def sample_game_data():
    """Sample game data from API"""
    return {
        "id": "test123",
        "rated": True,
        "variant": "standard",
        "speed": "blitz",
        "players": {
            "white": {"user": {"name": "Player1"}, "rating": 1500},
            "black": {"user": {"name": "Player2"}, "rating": 1520}
        },
        "winner": "white",
        "moves": "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7",
        "opening": {
            "eco": "C88",
            "name": "Ruy Lopez: Closed"
        }
    }


@pytest.fixture
def sample_avatar_config():
    """Sample avatar configuration"""
    return {
        "name": "TestAvatar",
        "platform": "lichess",
        "username": "testplayer",
        "elo": 1500,
        "games_analyzed": 100,
        "style": {
            "aggressive_score": 45,
            "avg_game_length": 40,
            "favorite_openings": ["e4", "d4"],
            "blunder_rate": 5.2
        },
        "stockfish_config": {
            "skill_level": 10,
            "depth": 15,
            "contempt": 0
        }
    }


@pytest.fixture
def temp_config_file(tmp_path):
    """Create temporary config file"""
    config_file = tmp_path / "test_config.json"
    return config_file


@pytest.fixture
def mock_engine_path():
    """Mock engine path (doesn't need to exist for most tests)"""
    return "/mock/path/to/stockfish.exe"


# Cleanup after tests
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Cleanup any temporary files created during tests"""
    yield
    # Cleanup code runs after each test
    # Add cleanup logic if needed

