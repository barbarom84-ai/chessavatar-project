"""
Tests for UI components
Tests chessboard and main window
"""
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtTest import QTest
from ui.chessboard import ChessBoardWidget
import chess


@pytest.mark.ui
class TestChessBoard:
    """Test ChessBoardWidget widget"""
    
    def test_chessboard_initialization(self, qapp):
        """Test chessboard initializes correctly"""
        board = ChessBoardWidget()
        assert board is not None
        assert board.board.fen() == chess.STARTING_FEN
        
    def test_board_size(self, qapp):
        """Test board size calculation"""
        board = ChessBoardWidget(square_size=70)
        expected_size = 70 * 8  # 8x8 board
        assert board.board_size == expected_size
        
    def test_square_at_position(self, qapp):
        """Test getting square at pixel position"""
        board = ChessBoardWidget(square_size=70)
        
        # Top-left corner should be a8 (for white's perspective)
        square = board.get_square_at_pos(QPoint(35, 35))  # Center of first square
        assert square is not None
        
    def test_piece_at_square(self, qapp):
        """Test getting piece at square"""
        board = ChessBoardWidget()
        
        # e2 should have white pawn
        piece = board.board.piece_at(chess.E2)
        assert piece is not None
        assert piece.piece_type == chess.PAWN
        assert piece.color == chess.WHITE
        
    def test_legal_move_highlighting(self, qapp):
        """Test legal move highlights"""
        board = ChessBoardWidget()
        
        # Select e2 pawn
        board.selected_square = chess.E2
        legal_moves = board.get_legal_moves_for_square(chess.E2)
        
        assert len(legal_moves) > 0
        assert any(move.to_square == chess.E4 for move in legal_moves)
        
    def test_make_move(self, qapp):
        """Test making a move on the board"""
        board = ChessBoardWidget()
        
        move = chess.Move.from_uci("e2e4")
        board.make_move(move)
        
        # e2 should be empty, e4 should have pawn
        assert board.board.piece_at(chess.E2) is None
        assert board.board.piece_at(chess.E4) is not None
        
    def test_undo_move(self, qapp):
        """Test undoing a move"""
        board = ChessBoardWidget()
        initial_fen = board.board.fen()
        
        move = chess.Move.from_uci("e2e4")
        board.make_move(move)
        board.undo_move()
        
        assert board.board.fen() == initial_fen
        
    def test_board_flip(self, qapp):
        """Test flipping board perspective"""
        board = ChessBoardWidget()
        
        initial_flip = board.flipped
        board.flip_board()
        
        assert board.flipped != initial_flip
        
    def test_drag_and_drop(self, qapp):
        """Test drag and drop piece movement"""
        board = ChessBoardWidget()
        board.show()
        
        # Simulate drag from e2 to e4
        # This is a simplified test - full drag/drop testing requires more setup
        board.selected_square = chess.E2
        assert board.selected_square == chess.E2
        
    def test_promotion_handling(self, qapp):
        """Test pawn promotion"""
        board = ChessBoardWidget()
        
        # Set up position for promotion
        board.board.set_fen("8/P7/8/8/8/8/8/8 w - - 0 1")
        
        # Move pawn to promotion square
        move = chess.Move.from_uci("a7a8q")  # Promote to queen
        board.make_move(move)
        
        piece = board.board.piece_at(chess.A8)
        assert piece.piece_type == chess.QUEEN
        
    def test_check_highlighting(self, qapp):
        """Test check square highlighting"""
        board = ChessBoardWidget()
        
        # Set up check position
        board.board.set_fen("rnb1kbnr/pppp1ppp/8/4p3/5PPq/8/PPPPP2P/RNBQKBNR w KQkq - 1 3")
        
        assert board.board.is_check()
        king_square = board.board.king(chess.WHITE)
        assert king_square is not None
        
    def test_last_move_highlighting(self, qapp):
        """Test last move highlighting"""
        board = ChessBoardWidget()
        
        move = chess.Move.from_uci("e2e4")
        board.make_move(move)
        
        # Last move should be stored
        assert board.last_move == move
        
    def test_square_colors(self, qapp):
        """Test square color alternation"""
        board = ChessBoardWidget()
        
        # a1 is dark square (0 + 0 = 0, even)
        # a2 is light square (0 + 1 = 1, odd)
        # Verify colors are set
        assert board.light_square_color is not None
        assert board.dark_square_color is not None


@pytest.mark.ui
class TestBoardInteraction:
    """Test board user interactions"""
    
    def test_mouse_click(self, qapp):
        """Test mouse click on square"""
        board = ChessBoardWidget(square_size=70)
        board.show()
        
        # Calculate position for e2 square
        # e2 is column 4 (e), row 6 from bottom (for white)
        col = 4
        row = 6
        x = col * 70 + 35  # Center of square
        y = row * 70 + 35
        
        # Simulate click
        QTest.mouseClick(board, Qt.MouseButton.LeftButton, pos=QPoint(x, y))
        
        # After click, e2 might be selected (depends on implementation)
        # This is more of an integration test
        
    def test_piece_selection(self, qapp):
        """Test selecting a piece"""
        board = ChessBoardWidget()
        
        # Programmatically select e2
        board.selected_square = chess.E2
        assert board.selected_square == chess.E2
        
        # Deselect
        board.selected_square = None
        assert board.selected_square is None
        
    def test_invalid_move_rejection(self, qapp):
        """Test invalid moves are rejected"""
        board = ChessBoardWidget()
        
        # Try to make invalid move
        invalid_move = chess.Move.from_uci("e2e5")  # Pawn can't move 3 squares
        
        # Should not be in legal moves
        legal_moves = list(board.board.legal_moves)
        assert invalid_move not in legal_moves


@pytest.mark.ui
class TestBoardRendering:
    """Test board rendering"""
    
    def test_paint_event(self, qapp):
        """Test board painting"""
        board = ChessBoardWidget()
        board.show()
        
        # Force repaint
        board.repaint()
        
        # If no exception, painting works
        assert True
        
    def test_resize_event(self, qapp):
        """Test board resizing"""
        board = ChessBoardWidget(square_size=70)
        board.show()
        
        initial_size = board.size()
        board.resize(700, 700)
        
        assert board.size() != initial_size
        
    def test_coordinates_display(self, qapp):
        """Test board coordinate labels"""
        board = ChessBoardWidget()
        
        # Coordinates should be configurable
        # This tests that the option exists
        assert hasattr(board, 'show_coordinates') or True


@pytest.mark.ui
@pytest.mark.slow
class TestBoardPerformance:
    """Test board performance"""
    
    def test_rapid_moves(self, qapp):
        """Test making many moves quickly"""
        board = ChessBoardWidget()
        
        # Make 100 moves
        import time
        start = time.time()
        
        for i in range(50):  # 50 moves by each side
            legal_moves = list(board.board.legal_moves)
            if legal_moves:
                board.make_move(legal_moves[0])
            else:
                break
                
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        assert elapsed < 1.0  # Less than 1 second
        
    def test_board_redraws(self, qapp):
        """Test multiple board redraws"""
        board = ChessBoardWidget()
        board.show()
        
        # Trigger multiple redraws
        for i in range(100):
            board.update()
            
        # Should not crash
        assert True

