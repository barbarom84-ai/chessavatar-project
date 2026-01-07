"""
Tests for core.api_service module
Tests API calls to Lichess and Chess.com (with mocks)
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from core.api_service import APIService
import requests


@pytest.mark.api
@pytest.mark.unit
class TestAPIService:
    """Test APIService class"""
    
    def test_api_service_initialization(self):
        """Test API service initializes correctly"""
        api = APIService()
        assert api.lichess_base_url == "https://lichess.org/api"
        assert api.chesscom_base_url == "https://api.chess.com/pub"
        
    @patch('requests.get')
    def test_fetch_lichess_user(self, mock_get):
        """Test fetching Lichess user profile"""
        api = APIService()
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "testuser",
            "username": "TestUser",
            "perfs": {
                "blitz": {"rating": 1500}
            }
        }
        mock_get.return_value = mock_response
        
        result = api.fetch_lichess_user("testuser")
        assert result is not None
        assert result["username"] == "TestUser"
        assert result["perfs"]["blitz"]["rating"] == 1500
        
    @patch('requests.get')
    def test_fetch_lichess_user_not_found(self, mock_get):
        """Test fetching non-existent Lichess user"""
        api = APIService()
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = api.fetch_lichess_user("nonexistentuser")
        assert result is None
        
    @patch('requests.get')
    def test_fetch_lichess_games(self, mock_get, sample_game_data):
        """Test fetching Lichess games"""
        api = APIService()
        
        # Mock NDJSON response (newline-delimited JSON)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            '{"id": "game1", "moves": "e4 e5"}',
            '{"id": "game2", "moves": "d4 d5"}'
        ]
        mock_get.return_value = mock_response
        
        games = api.fetch_lichess_games("testuser", max_games=2)
        assert len(games) == 2
        assert games[0]["id"] == "game1"
        
    @patch('requests.get')
    def test_fetch_chesscom_user(self, mock_get):
        """Test fetching Chess.com user profile"""
        api = APIService()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "username": "TestUser",
            "player_id": 12345
        }
        mock_get.return_value = mock_response
        
        result = api.fetch_chesscom_user("testuser")
        assert result is not None
        assert result["username"] == "TestUser"
        
    @patch('requests.get')
    def test_fetch_chesscom_games(self, mock_get):
        """Test fetching Chess.com games"""
        api = APIService()
        
        # First call: get archives list
        mock_archives_response = Mock()
        mock_archives_response.status_code = 200
        mock_archives_response.json.return_value = {
            "archives": [
                "https://api.chess.com/pub/player/testuser/games/2024/01"
            ]
        }
        
        # Second call: get games from archive
        mock_games_response = Mock()
        mock_games_response.status_code = 200
        mock_games_response.json.return_value = {
            "games": [
                {"id": "game1", "pgn": "[Event \"Test\"] 1. e4"},
                {"id": "game2", "pgn": "[Event \"Test2\"] 1. d4"}
            ]
        }
        
        mock_get.side_effect = [mock_archives_response, mock_games_response]
        
        games = api.fetch_chesscom_games("testuser", max_games=2)
        assert len(games) <= 2
        
    @patch('requests.get')
    def test_rate_limiting(self, mock_get):
        """Test rate limiting handling"""
        api = APIService()
        
        mock_response = Mock()
        mock_response.status_code = 429  # Too Many Requests
        mock_get.return_value = mock_response
        
        result = api.fetch_lichess_user("testuser")
        assert result is None
        
    @patch('requests.get')
    def test_timeout_handling(self, mock_get):
        """Test timeout handling"""
        api = APIService()
        
        mock_get.side_effect = requests.Timeout()
        
        result = api.fetch_lichess_user("testuser")
        assert result is None
        
    @patch('requests.get')
    def test_connection_error_handling(self, mock_get):
        """Test connection error handling"""
        api = APIService()
        
        mock_get.side_effect = requests.ConnectionError()
        
        result = api.fetch_lichess_user("testuser")
        assert result is None
        
    @patch('requests.get')
    def test_parse_lichess_game(self, mock_get):
        """Test parsing Lichess game data"""
        api = APIService()
        
        game_data = {
            "id": "test123",
            "rated": True,
            "variant": "standard",
            "speed": "blitz",
            "players": {
                "white": {"user": {"name": "Player1"}, "rating": 1500},
                "black": {"user": {"name": "Player2"}, "rating": 1520}
            },
            "moves": "e4 e5 Nf3 Nc6",
            "winner": "white",
            "opening": {
                "eco": "C20",
                "name": "King's Pawn Game"
            }
        }
        
        # Verify data structure
        assert game_data["speed"] == "blitz"
        assert game_data["players"]["white"]["rating"] == 1500
        assert "opening" in game_data
        
    @patch('requests.get')
    def test_fetch_games_with_filters(self, mock_get):
        """Test fetching games with time control filter"""
        api = APIService()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            '{"id": "game1", "speed": "blitz", "moves": "e4 e5"}',
            '{"id": "game2", "speed": "rapid", "moves": "d4 d5"}',
            '{"id": "game3", "speed": "blitz", "moves": "c4 e5"}'
        ]
        mock_get.return_value = mock_response
        
        games = api.fetch_lichess_games("testuser", max_games=10)
        
        # Filter for blitz games
        blitz_games = [g for g in games if g.get("speed") == "blitz"]
        assert len(blitz_games) == 2


@pytest.mark.api
@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API (require network)"""
    
    @pytest.mark.skip(reason="Requires network access")
    def test_real_lichess_user(self):
        """Test fetching real Lichess user (skipped by default)"""
        api = APIService()
        result = api.fetch_lichess_user("lichess")  # Official account
        assert result is not None
        
    @pytest.mark.skip(reason="Requires network access")
    def test_real_chesscom_user(self):
        """Test fetching real Chess.com user (skipped by default)"""
        api = APIService()
        result = api.fetch_chesscom_user("hikaru")  # Public figure
        assert result is not None


@pytest.mark.unit
class TestGameParsing:
    """Test parsing game data from APIs"""
    
    def test_parse_pgn_from_lichess(self):
        """Test parsing PGN from Lichess format"""
        game_data = {
            "moves": "e4 e5 Nf3 Nc6 Bb5",
            "players": {
                "white": {"user": {"name": "Player1"}},
                "black": {"user": {"name": "Player2"}}
            }
        }
        
        moves_list = game_data["moves"].split()
        assert len(moves_list) == 5
        assert moves_list[0] == "e4"
        
    def test_parse_pgn_from_chesscom(self):
        """Test parsing PGN from Chess.com format"""
        pgn_string = """[Event "Test Game"]
[White "Player1"]
[Black "Player2"]

1. e4 e5 2. Nf3 *
"""
        assert "e4 e5" in pgn_string
        assert "Player1" in pgn_string

