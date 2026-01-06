"""
PGN Import/Export functionality
"""
import chess
import chess.pgn
from io import StringIO
from pathlib import Path
from typing import Optional, List
from datetime import datetime


class PGNManager:
    """Manager for PGN import and export"""
    
    def __init__(self):
        self.last_import_path: Optional[Path] = None
        self.last_export_path: Optional[Path] = None
        
    def export_game(
        self,
        board: chess.Board,
        move_history: List[str],
        filename: str,
        white_player: str = "White",
        black_player: str = "Black",
        event: str = "Casual Game",
        site: str = "ChessAvatar",
        result: str = "*"
    ) -> bool:
        """
        Export current game to PGN file
        
        Args:
            board: Current chess board
            move_history: List of moves in SAN notation
            filename: Output filename
            white_player: White player name
            black_player: Black player name
            event: Event name
            site: Site name
            result: Game result (1-0, 0-1, 1/2-1/2, *)
            
        Returns:
            True if export successful
        """
        try:
            # Create a new game
            game = chess.pgn.Game()
            
            # Set headers
            game.headers["Event"] = event
            game.headers["Site"] = site
            game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
            game.headers["Round"] = "?"
            game.headers["White"] = white_player
            game.headers["Black"] = black_player
            game.headers["Result"] = result
            
            # Reconstruct the game from move history
            node = game
            temp_board = chess.Board()
            
            for move_san in move_history:
                try:
                    move = temp_board.parse_san(move_san)
                    node = node.add_variation(move)
                    temp_board.push(move)
                except:
                    break
                    
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                exporter = chess.pgn.FileExporter(f)
                game.accept(exporter)
                
            self.last_export_path = Path(filename)
            return True
            
        except Exception as e:
            print(f"Error exporting PGN: {e}")
            return False
            
    def export_game_complete(
        self,
        game_pgn: str,
        filename: str
    ) -> bool:
        """
        Export a complete PGN string to file
        
        Args:
            game_pgn: Complete PGN string
            filename: Output filename
            
        Returns:
            True if export successful
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(game_pgn)
                
            self.last_export_path = Path(filename)
            return True
            
        except Exception as e:
            print(f"Error exporting PGN: {e}")
            return False
            
    def import_game(self, filename: str) -> Optional[chess.pgn.Game]:
        """
        Import game from PGN file
        
        Args:
            filename: PGN file path
            
        Returns:
            chess.pgn.Game object or None if error
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                game = chess.pgn.read_game(f)
                
            if game:
                self.last_import_path = Path(filename)
                
            return game
            
        except Exception as e:
            print(f"Error importing PGN: {e}")
            return None
            
    def import_games(self, filename: str) -> List[chess.pgn.Game]:
        """
        Import multiple games from PGN file
        
        Args:
            filename: PGN file path
            
        Returns:
            List of chess.pgn.Game objects
        """
        games = []
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                while True:
                    game = chess.pgn.read_game(f)
                    if game is None:
                        break
                    games.append(game)
                    
            if games:
                self.last_import_path = Path(filename)
                
        except Exception as e:
            print(f"Error importing PGN: {e}")
            
        return games
        
    def parse_pgn_string(self, pgn_string: str) -> Optional[chess.pgn.Game]:
        """
        Parse PGN from string
        
        Args:
            pgn_string: PGN text
            
        Returns:
            chess.pgn.Game object or None
        """
        try:
            pgn_io = StringIO(pgn_string)
            game = chess.pgn.read_game(pgn_io)
            return game
        except Exception as e:
            print(f"Error parsing PGN: {e}")
            return None
            
    def game_to_move_list(self, game: chess.pgn.Game) -> List[str]:
        """
        Extract move list from game
        
        Args:
            game: chess.pgn.Game object
            
        Returns:
            List of moves in SAN notation
        """
        moves = []
        
        try:
            board = game.board()
            for move in game.mainline_moves():
                san = board.san(move)
                moves.append(san)
                board.push(move)
        except Exception as e:
            print(f"Error extracting moves: {e}")
            
        return moves
        
    def get_game_info(self, game: chess.pgn.Game) -> dict:
        """
        Extract game information
        
        Args:
            game: chess.pgn.Game object
            
        Returns:
            Dictionary with game info
        """
        return {
            'event': game.headers.get('Event', 'Unknown'),
            'site': game.headers.get('Site', 'Unknown'),
            'date': game.headers.get('Date', 'Unknown'),
            'round': game.headers.get('Round', '?'),
            'white': game.headers.get('White', 'Unknown'),
            'black': game.headers.get('Black', 'Unknown'),
            'result': game.headers.get('Result', '*'),
            'white_elo': game.headers.get('WhiteElo', '?'),
            'black_elo': game.headers.get('BlackElo', '?'),
            'eco': game.headers.get('ECO', '?'),
            'opening': game.headers.get('Opening', '?'),
        }
        
    def validate_pgn_file(self, filename: str) -> tuple[bool, str]:
        """
        Validate PGN file format
        
        Args:
            filename: PGN file path
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if not content.strip():
                return False, "File is empty"
                
            # Try to parse at least one game
            pgn_io = StringIO(content)
            game = chess.pgn.read_game(pgn_io)
            
            if game is None:
                return False, "No valid game found in PGN"
                
            return True, "Valid PGN file"
            
        except Exception as e:
            return False, f"Error reading file: {str(e)}"


# Singleton instance
_pgn_manager: Optional[PGNManager] = None


def get_pgn_manager() -> PGNManager:
    """Get the global PGN manager instance"""
    global _pgn_manager
    if _pgn_manager is None:
        _pgn_manager = PGNManager()
    return _pgn_manager

