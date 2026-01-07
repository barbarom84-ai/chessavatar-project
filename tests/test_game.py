"""
Unit tests for core.game module
Tests chess game logic and state management
"""
import pytest
import chess
from core.game import ChessGame


@pytest.mark.unit
class TestChessGame:
    """Test ChessGame class"""
    
    def test_game_initialization(self):
        """Test game initializes with correct starting position"""
        game = ChessGame()
        assert game.board.fen() == chess.STARTING_FEN
        assert len(game.move_history) == 0
        assert game.result is None
        
    def test_valid_move(self):
        """Test making a valid move"""
        game = ChessGame()
        move = chess.Move.from_uci("e2e4")
        assert game.is_move_legal(move)
        game.make_move(move)
        assert len(game.move_history) == 1
        assert game.move_history[0] == move
        
    def test_invalid_move(self):
        """Test invalid move is rejected"""
        game = ChessGame()
        move = chess.Move.from_uci("e2e5")  # Invalid: pawn can't move 3 squares
        assert not game.is_move_legal(move)
        
    def test_undo_move(self):
        """Test undoing a move"""
        game = ChessGame()
        initial_fen = game.board.fen()
        move = chess.Move.from_uci("e2e4")
        game.make_move(move)
        game.undo_move()
        assert game.board.fen() == initial_fen
        assert len(game.move_history) == 0
        
    def test_redo_move(self):
        """Test redoing a move"""
        game = ChessGame()
        move = chess.Move.from_uci("e2e4")
        game.make_move(move)
        fen_after_move = game.board.fen()
        game.undo_move()
        game.redo_move()
        assert game.board.fen() == fen_after_move
        
    def test_get_legal_moves(self):
        """Test getting legal moves for a square"""
        game = ChessGame()
        # e2 pawn can move to e3 or e4
        legal_moves = game.get_legal_moves(chess.E2)
        move_ucis = [move.uci() for move in legal_moves]
        assert "e2e3" in move_ucis
        assert "e2e4" in move_ucis
        
    def test_is_check(self):
        """Test check detection"""
        game = ChessGame()
        # Set up a check position
        game.board.set_fen("rnb1kbnr/pppp1ppp/8/4p3/5PPq/8/PPPPP2P/RNBQKBNR w KQkq - 1 3")
        assert game.is_check()
        
    def test_is_checkmate(self):
        """Test checkmate detection"""
        game = ChessGame()
        # Fool's mate
        game.board.set_fen("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")
        assert game.is_checkmate()
        
    def test_is_stalemate(self):
        """Test stalemate detection"""
        game = ChessGame()
        # Simple stalemate position
        game.board.set_fen("k7/8/1K6/8/8/8/8/7Q b - - 0 1")
        assert game.is_stalemate()
        
    def test_get_game_result(self):
        """Test game result determination"""
        game = ChessGame()
        # Checkmate position
        game.board.set_fen("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")
        result = game.get_game_result()
        assert result == "0-1"  # Black wins
        
    def test_reset_game(self):
        """Test game reset"""
        game = ChessGame()
        game.make_move(chess.Move.from_uci("e2e4"))
        game.make_move(chess.Move.from_uci("e7e5"))
        game.reset()
        assert game.board.fen() == chess.STARTING_FEN
        assert len(game.move_history) == 0
        
    def test_load_from_fen(self):
        """Test loading position from FEN"""
        game = ChessGame()
        test_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        game.load_from_fen(test_fen)
        assert game.board.fen() == test_fen
        
    def test_get_san_notation(self):
        """Test SAN notation generation"""
        game = ChessGame()
        move = chess.Move.from_uci("e2e4")
        san = game.get_san_notation(move)
        assert san == "e4"
        
    def test_move_sequence(self):
        """Test a sequence of moves (Scholar's mate)"""
        game = ChessGame()
        moves = ["e2e4", "e7e5", "f1c4", "b8c6", "d1h5", "g8f6", "h5f7"]
        
        for move_uci in moves[:-1]:
            move = chess.Move.from_uci(move_uci)
            assert game.is_move_legal(move)
            game.make_move(move)
            
        # Final move should be checkmate
        final_move = chess.Move.from_uci(moves[-1])
        game.make_move(final_move)
        assert game.is_checkmate()
        
    def test_fifty_move_rule(self):
        """Test fifty-move rule detection"""
        game = ChessGame()
        # Set a position near 50-move rule
        game.board.set_fen("8/8/8/8/8/4k3/4K3/8 w - - 99 100")
        assert game.board.can_claim_fifty_moves()
        
    def test_threefold_repetition(self):
        """Test threefold repetition detection"""
        game = ChessGame()
        # Make moves that repeat position
        moves = ["g1f3", "g8f6", "f3g1", "f6g8", "g1f3", "g8f6", "f3g1", "f6g8"]
        for move_uci in moves:
            game.make_move(chess.Move.from_uci(move_uci))
        assert game.board.can_claim_threefold_repetition()


@pytest.mark.unit
class TestGameState:
    """Test game state management"""
    
    def test_turn_tracking(self):
        """Test turn switches correctly"""
        game = ChessGame()
        assert game.board.turn == chess.WHITE
        game.make_move(chess.Move.from_uci("e2e4"))
        assert game.board.turn == chess.BLACK
        game.make_move(chess.Move.from_uci("e7e5"))
        assert game.board.turn == chess.WHITE
        
    def test_castling_rights(self):
        """Test castling rights are tracked"""
        game = ChessGame()
        assert game.board.has_kingside_castling_rights(chess.WHITE)
        assert game.board.has_queenside_castling_rights(chess.WHITE)
        
    def test_en_passant(self):
        """Test en passant capture"""
        game = ChessGame()
        # Set up en passant position
        game.board.set_fen("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3")
        en_passant_move = chess.Move.from_uci("e5d6")
        assert game.is_move_legal(en_passant_move)
        game.make_move(en_passant_move)
        # Verify the pawn was captured
        assert game.board.piece_at(chess.D5) is None


@pytest.mark.unit
class TestGameAnalysis:
    """Test game analysis features"""
    
    def test_material_count(self):
        """Test material counting"""
        game = ChessGame()
        # Starting position should have equal material
        # Q=9, R=5, B=3, N=3, P=1
        white_material = sum([
            len(game.board.pieces(chess.QUEEN, chess.WHITE)) * 9,
            len(game.board.pieces(chess.ROOK, chess.WHITE)) * 5,
            len(game.board.pieces(chess.BISHOP, chess.WHITE)) * 3,
            len(game.board.pieces(chess.KNIGHT, chess.WHITE)) * 3,
            len(game.board.pieces(chess.PAWN, chess.WHITE)) * 1
        ])
        black_material = sum([
            len(game.board.pieces(chess.QUEEN, chess.BLACK)) * 9,
            len(game.board.pieces(chess.ROOK, chess.BLACK)) * 5,
            len(game.board.pieces(chess.BISHOP, chess.BLACK)) * 3,
            len(game.board.pieces(chess.KNIGHT, chess.BLACK)) * 3,
            len(game.board.pieces(chess.PAWN, chess.BLACK)) * 1
        ])
        assert white_material == black_material == 39
        
    def test_move_count(self):
        """Test move counting"""
        game = ChessGame()
        assert game.board.fullmove_number == 1
        game.make_move(chess.Move.from_uci("e2e4"))
        assert game.board.fullmove_number == 1  # Still move 1 (Black hasn't moved)
        game.make_move(chess.Move.from_uci("e7e5"))
        assert game.board.fullmove_number == 2  # Now move 2

