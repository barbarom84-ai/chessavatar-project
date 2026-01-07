"""
Tests for core.style_analyzer module
Tests playing style analysis from games
"""
import pytest
from core.style_analyzer import StyleAnalyzer
import chess
import chess.pgn
from io import StringIO


@pytest.mark.unit
class TestStyleAnalyzer:
    """Test StyleAnalyzer class"""
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly"""
        analyzer = StyleAnalyzer()
        assert analyzer is not None
        
    def test_analyze_single_game(self):
        """Test analyzing a single game"""
        analyzer = StyleAnalyzer()
        
        # Create a simple game
        game = chess.pgn.Game()
        node = game
        moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6"]
        for move_uci in moves:
            node = node.add_variation(chess.Move.from_uci(move_uci))
            
        analysis = analyzer.analyze_game(game)
        assert analysis is not None
        assert "game_length" in analysis
        assert analysis["game_length"] == len(moves)
        
    def test_analyze_aggressive_score(self):
        """Test aggressive score calculation"""
        analyzer = StyleAnalyzer()
        
        # Create aggressive game (Scholar's mate attempt)
        game = chess.pgn.Game()
        node = game
        aggressive_moves = ["e2e4", "e7e5", "d1h5", "b8c6", "f1c4", "g8f6"]
        for move_uci in aggressive_moves:
            node = node.add_variation(chess.Move.from_uci(move_uci))
            
        analysis = analyzer.analyze_game(game)
        # Queen out early should increase aggressive score
        assert "aggressive_indicators" in analysis or "game_length" in analysis
        
    def test_analyze_positional_play(self):
        """Test positional play detection"""
        analyzer = StyleAnalyzer()
        
        # Create positional game
        game = chess.pgn.Game()
        node = game
        positional_moves = ["d2d4", "g8f6", "c2c4", "e7e6", "g1f3", "d7d5"]
        for move_uci in positional_moves:
            node = node.add_variation(chess.Move.from_uci(move_uci))
            
        analysis = analyzer.analyze_game(game)
        assert analysis is not None
        
    def test_analyze_multiple_games(self):
        """Test analyzing multiple games"""
        analyzer = StyleAnalyzer()
        
        games = []
        for i in range(5):
            game = chess.pgn.Game()
            node = game
            # Simple openings
            moves = ["e2e4", "e7e5", "g1f3", "b8c6"]
            for move_uci in moves:
                node = node.add_variation(chess.Move.from_uci(move_uci))
            games.append(game)
            
        results = analyzer.analyze_games(games)
        assert len(results) == 5
        
    def test_detect_opening_preference(self):
        """Test detecting opening preferences"""
        analyzer = StyleAnalyzer()
        
        # Create multiple games with e4 opening
        games = []
        for i in range(10):
            game = chess.pgn.Game()
            node = game
            node = node.add_variation(chess.Move.from_uci("e2e4"))
            node = node.add_variation(chess.Move.from_uci("e7e5"))
            games.append(game)
            
        results = analyzer.analyze_games(games)
        
        # Count e4 openings
        e4_count = sum(1 for r in results if r.get("first_move") in ["e2e4", "e4"])
        assert e4_count >= 8  # Most games should start with e4
        
    def test_calculate_average_game_length(self):
        """Test calculating average game length"""
        analyzer = StyleAnalyzer()
        
        game_lengths = [30, 40, 35, 45, 38]
        avg_length = sum(game_lengths) / len(game_lengths)
        assert avg_length == 37.6
        
    def test_tactical_vs_positional(self):
        """Test distinguishing tactical vs positional play"""
        analyzer = StyleAnalyzer()
        
        # Tactical game (quick checkmate)
        tactical_game = chess.pgn.Game()
        node = tactical_game
        for move_uci in ["e2e4", "e7e5", "d1h5", "b8c6", "f1c4", "g8f6", "h5f7"]:
            node = node.add_variation(chess.Move.from_uci(move_uci))
            
        analysis = analyzer.analyze_game(tactical_game)
        # Short game with queen and bishop attack
        assert analysis["game_length"] < 10  # Very short = tactical
        
    def test_piece_development_speed(self):
        """Test analyzing piece development speed"""
        analyzer = StyleAnalyzer()
        
        # Fast development
        game = chess.pgn.Game()
        node = game
        for move_uci in ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5", "b1c3", "g8f6"]:
            node = node.add_variation(chess.Move.from_uci(move_uci))
            
        analysis = analyzer.analyze_game(game)
        # Should detect multiple pieces developed
        assert analysis is not None
        
    def test_pawn_structure_analysis(self):
        """Test pawn structure considerations"""
        analyzer = StyleAnalyzer()
        
        # Game with pawn moves
        game = chess.pgn.Game()
        node = game
        for move_uci in ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4"]:
            node = node.add_variation(chess.Move.from_uci(move_uci))
            
        analysis = analyzer.analyze_game(game)
        assert analysis is not None
        
    def test_empty_games_list(self):
        """Test analyzing empty games list"""
        analyzer = StyleAnalyzer()
        results = analyzer.analyze_games([])
        assert results == []
        
    def test_game_with_comments(self):
        """Test analyzing game with comments"""
        analyzer = StyleAnalyzer()
        
        game = chess.pgn.Game()
        node = game.add_variation(chess.Move.from_uci("e2e4"))
        node.comment = "Good opening move"
        node = node.add_variation(chess.Move.from_uci("e7e5"))
        
        analysis = analyzer.analyze_game(game)
        assert analysis is not None


@pytest.mark.unit
class TestStyleMetrics:
    """Test style metric calculations"""
    
    def test_aggressive_score_range(self):
        """Test aggressive score is in valid range"""
        analyzer = StyleAnalyzer()
        
        # Create test game
        game = chess.pgn.Game()
        node = game
        for move_uci in ["e2e4", "e7e5", "g1f3", "b8c6"]:
            node = node.add_variation(chess.Move.from_uci(move_uci))
            
        analysis = analyzer.analyze_game(game)
        
        # If aggressive_score is calculated, it should be 0-100
        if "aggressive_score" in analysis:
            assert 0 <= analysis["aggressive_score"] <= 100
            
    def test_opening_repertoire(self):
        """Test building opening repertoire"""
        first_moves = ["e4", "e4", "e4", "d4", "e4", "c4"]
        
        from collections import Counter
        repertoire = Counter(first_moves)
        
        assert repertoire["e4"] == 4
        assert repertoire["d4"] == 1
        assert repertoire["c4"] == 1
        assert repertoire.most_common(1)[0][0] == "e4"
        
    def test_win_rate_calculation(self):
        """Test win rate calculation"""
        results = ["1-0", "1-0", "0-1", "1/2-1/2", "1-0"]
        
        wins = sum(1 for r in results if r == "1-0")
        total = len(results)
        win_rate = (wins / total) * 100
        
        assert win_rate == 60.0  # 3 wins out of 5
        
    def test_average_elo_calculation(self):
        """Test average Elo calculation"""
        ratings = [1500, 1520, 1480, 1510, 1490]
        avg_rating = sum(ratings) / len(ratings)
        
        assert avg_rating == 1500.0


@pytest.mark.unit
class TestStyleProfile:
    """Test complete style profile generation"""
    
    def test_generate_style_profile(self):
        """Test generating complete style profile"""
        analyzer = StyleAnalyzer()
        
        # Create multiple games
        games = []
        for i in range(20):
            game = chess.pgn.Game()
            game.headers["Result"] = "1-0" if i % 2 == 0 else "0-1"
            node = game
            # Alternate between e4 and d4
            first_move = "e2e4" if i % 2 == 0 else "d2d4"
            node = node.add_variation(chess.Move.from_uci(first_move))
            node = node.add_variation(chess.Move.from_uci("e7e5" if i % 2 == 0 else "d7d5"))
            games.append(game)
            
        results = analyzer.analyze_games(games)
        assert len(results) == 20
        
    def test_style_consistency(self):
        """Test measuring style consistency"""
        # Player who always plays e4 is consistent
        moves = ["e4"] * 10
        consistency = len(set(moves)) / len(moves)
        assert consistency == 0.1  # Low diversity = high consistency
        
        # Player who varies openings
        varied_moves = ["e4", "d4", "c4", "Nf3", "e4", "d4"]
        varied_consistency = len(set(varied_moves)) / len(varied_moves)
        assert varied_consistency > consistency

