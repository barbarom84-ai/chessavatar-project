"""
Game logic wrapper using python-chess library
"""
import chess
from typing import Optional, List


class ChessGame:
    """Wrapper class for chess game logic"""
    
    def __init__(self):
        self.board = chess.Board()
        self.move_history: List[str] = []
        
    def reset(self):
        """Reset the game to initial position"""
        self.board.reset()
        self.move_history.clear()
        
    def make_move(self, move: chess.Move) -> bool:
        """
        Make a move on the board
        
        Args:
            move: Chess move to make
            
        Returns:
            True if move was legal and made, False otherwise
        """
        if move in self.board.legal_moves:
            san = self.board.san(move)
            self.board.push(move)
            self.move_history.append(san)
            return True
        return False
        
    def make_move_uci(self, uci_move: str) -> bool:
        """
        Make a move using UCI notation (e.g., "e2e4")
        
        Args:
            uci_move: Move in UCI format
            
        Returns:
            True if move was legal and made, False otherwise
        """
        try:
            move = chess.Move.from_uci(uci_move)
            return self.make_move(move)
        except ValueError:
            return False
            
    def get_legal_moves(self, square: Optional[int] = None) -> List[chess.Move]:
        """
        Get legal moves from a square or all legal moves
        
        Args:
            square: Chess square index (0-63) or None for all moves
            
        Returns:
            List of legal moves
        """
        if square is None:
            return list(self.board.legal_moves)
        return [move for move in self.board.legal_moves if move.from_square == square]
        
    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.board.is_game_over()
        
    def get_result(self) -> str:
        """Get game result string"""
        if self.board.is_checkmate():
            return "Checkmate"
        elif self.board.is_stalemate():
            return "Stalemate"
        elif self.board.is_insufficient_material():
            return "Draw - Insufficient material"
        elif self.board.is_fifty_moves():
            return "Draw - Fifty moves rule"
        elif self.board.is_repetition():
            return "Draw - Threefold repetition"
        return "Game in progress"
        
    def get_pgn_moves(self) -> str:
        """Get moves in PGN format"""
        pgn_text = ""
        for i, move in enumerate(self.move_history):
            if i % 2 == 0:
                pgn_text += f"{i//2 + 1}. {move} "
            else:
                pgn_text += f"{move} "
        return pgn_text.strip()
        
    def undo_move(self) -> bool:
        """Undo the last move"""
        if len(self.board.move_stack) > 0:
            self.board.pop()
            if self.move_history:
                self.move_history.pop()
            return True
        return False

