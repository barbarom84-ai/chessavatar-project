"""
Unit tests for core.pgn_manager module
Tests PGN import/export functionality
"""
import pytest
from pathlib import Path
from core.pgn_manager import PGNManager
import chess
import chess.pgn
from io import StringIO


@pytest.mark.unit
class TestPGNManager:
    """Test PGNManager class"""
    
    def test_parse_pgn_string(self, sample_pgn):
        """Test parsing PGN from string"""
        manager = PGNManager()
        game = manager.parse_pgn_string(sample_pgn)
        assert game is not None
        assert game.headers["Event"] == "Test Game"
        assert game.headers["White"] == "Player1"
        assert game.headers["Black"] == "Player2"
        assert game.headers["Result"] == "1-0"
        
    def test_parse_invalid_pgn(self):
        """Test parsing invalid PGN"""
        manager = PGNManager()
        invalid_pgn = "This is not a valid PGN"
        game = manager.parse_pgn_string(invalid_pgn)
        assert game is None
        
    def test_export_to_pgn_string(self):
        """Test exporting game to PGN string"""
        manager = PGNManager()
        
        # Create a simple game
        game = chess.pgn.Game()
        game.headers["Event"] = "Test Export"
        game.headers["White"] = "TestWhite"
        game.headers["Black"] = "TestBlack"
        game.headers["Result"] = "*"
        
        node = game
        node = node.add_variation(chess.Move.from_uci("e2e4"))
        node = node.add_variation(chess.Move.from_uci("e7e5"))
        
        pgn_string = manager.export_to_pgn_string(game)
        assert "Test Export" in pgn_string
        assert "TestWhite" in pgn_string
        assert "TestBlack" in pgn_string
        assert "1. e4 e5" in pgn_string
        
    def test_load_from_file(self, tmp_path, sample_pgn):
        """Test loading PGN from file"""
        manager = PGNManager()
        
        # Create temporary PGN file
        pgn_file = tmp_path / "test.pgn"
        pgn_file.write_text(sample_pgn)
        
        game = manager.load_from_file(str(pgn_file))
        assert game is not None
        assert game.headers["Event"] == "Test Game"
        
    def test_load_from_nonexistent_file(self):
        """Test loading from nonexistent file"""
        manager = PGNManager()
        game = manager.load_from_file("/nonexistent/file.pgn")
        assert game is None
        
    def test_save_to_file(self, tmp_path):
        """Test saving PGN to file"""
        manager = PGNManager()
        
        # Create a game
        game = chess.pgn.Game()
        game.headers["Event"] = "Save Test"
        game.headers["Result"] = "1-0"
        node = game.add_variation(chess.Move.from_uci("e2e4"))
        
        # Save to file
        pgn_file = tmp_path / "output.pgn"
        success = manager.save_to_file(game, str(pgn_file))
        assert success
        assert pgn_file.exists()
        
        # Verify content
        content = pgn_file.read_text()
        assert "Save Test" in content
        
    def test_extract_moves_from_game(self, sample_pgn):
        """Test extracting moves from PGN game"""
        manager = PGNManager()
        game = manager.parse_pgn_string(sample_pgn)
        
        moves = []
        node = game
        while node.variations:
            next_node = node.variation(0)
            moves.append(next_node.move)
            node = next_node
            
        assert len(moves) > 0
        assert moves[0] == chess.Move.from_uci("e2e4")
        
    def test_pgn_with_comments(self):
        """Test PGN with comments"""
        manager = PGNManager()
        pgn_with_comments = """[Event "Test"]
[Result "*"]

1. e4 {Good opening!} e5 2. Nf3 {Developing} *
"""
        game = manager.parse_pgn_string(pgn_with_comments)
        assert game is not None
        
        # Check first move has comment
        node = game.variation(0)
        assert "Good opening!" in node.comment
        
    def test_pgn_with_variations(self):
        """Test PGN with variations"""
        manager = PGNManager()
        pgn_with_vars = """[Event "Test"]
[Result "*"]

1. e4 e5 (1... c5 2. Nf3) 2. Nf3 *
"""
        game = manager.parse_pgn_string(pgn_with_vars)
        assert game is not None
        
        # Main line should have e5
        main_line = game.variation(0)
        assert main_line.move == chess.Move.from_uci("e7e5")
        
    def test_multiple_games_in_file(self, tmp_path):
        """Test loading multiple games from one file"""
        manager = PGNManager()
        
        pgn_content = """[Event "Game 1"]
[Result "1-0"]

1. e4 e5 1-0

[Event "Game 2"]
[Result "0-1"]

1. d4 d5 0-1
"""
        pgn_file = tmp_path / "multi.pgn"
        pgn_file.write_text(pgn_content)
        
        # Load first game
        game1 = manager.load_from_file(str(pgn_file))
        assert game1 is not None
        assert game1.headers["Event"] == "Game 1"
        
    def test_pgn_headers(self):
        """Test standard PGN headers"""
        manager = PGNManager()
        
        game = chess.pgn.Game()
        game.headers["Event"] = "Test Tournament"
        game.headers["Site"] = "Online"
        game.headers["Date"] = "2024.01.01"
        game.headers["Round"] = "1"
        game.headers["White"] = "Alice"
        game.headers["Black"] = "Bob"
        game.headers["Result"] = "1-0"
        game.headers["WhiteElo"] = "1500"
        game.headers["BlackElo"] = "1480"
        
        pgn_string = manager.export_to_pgn_string(game)
        
        assert "Test Tournament" in pgn_string
        assert "Alice" in pgn_string
        assert "Bob" in pgn_string
        assert "1500" in pgn_string
        
    def test_game_to_board(self, sample_pgn):
        """Test converting PGN game to board position"""
        manager = PGNManager()
        game = manager.parse_pgn_string(sample_pgn)
        
        # Get final position
        board = game.end().board()
        
        # Verify it's not the starting position
        assert board.fen() != chess.STARTING_FEN
        
    def test_export_with_result(self):
        """Test exporting game with result"""
        manager = PGNManager()
        
        game = chess.pgn.Game()
        game.headers["Result"] = "1-0"
        node = game
        node = node.add_variation(chess.Move.from_uci("e2e4"))
        node = node.add_variation(chess.Move.from_uci("e7e5"))
        node = node.add_variation(chess.Move.from_uci("d1h5"))
        node = node.add_variation(chess.Move.from_uci("b8c6"))
        node = node.add_variation(chess.Move.from_uci("f1c4"))
        node = node.add_variation(chess.Move.from_uci("g8f6"))
        node = node.add_variation(chess.Move.from_uci("h5f7"))  # Checkmate
        
        pgn_string = manager.export_to_pgn_string(game)
        assert "1-0" in pgn_string


@pytest.mark.unit
class TestPGNValidation:
    """Test PGN validation"""
    
    def test_valid_seven_tag_roster(self):
        """Test valid seven-tag roster"""
        pgn = """[Event "Test"]
[Site "Test Site"]
[Date "2024.01.01"]
[Round "1"]
[White "Alice"]
[Black "Bob"]
[Result "1-0"]

1. e4 1-0
"""
        manager = PGNManager()
        game = manager.parse_pgn_string(pgn)
        assert game is not None
        assert len(game.headers) >= 7
        
    def test_missing_required_tags(self):
        """Test PGN with missing tags still parses"""
        pgn = """[Event "Test"]

1. e4 *
"""
        manager = PGNManager()
        game = manager.parse_pgn_string(pgn)
        # Should still parse, just with default values for missing tags
        assert game is not None
        
    def test_illegal_move_sequence(self):
        """Test PGN with illegal moves"""
        # python-chess will reject illegal moves during parsing
        pgn = """[Event "Test"]
[Result "*"]

1. e4 e5 2. Ke2 *
"""
        manager = PGNManager()
        game = manager.parse_pgn_string(pgn)
        # Should parse legal moves up to the illegal one
        assert game is not None

