"""
Opening Book for ChessAvatar
ECO (Encyclopedia of Chess Openings) classification and opening recognition
"""
import chess
import json
from pathlib import Path
from typing import Optional, List, Dict, Tuple


class Opening:
    """Represents a chess opening"""
    
    def __init__(self, eco: str, name: str, moves: str, variation: str = ""):
        """
        Initialize an opening
        
        Args:
            eco: ECO code (e.g., "C50")
            name: Opening name (e.g., "Italian Game")
            moves: Move sequence in UCI format
            variation: Specific variation name
        """
        self.eco = eco
        self.name = name
        self.moves = moves  # Space-separated UCI moves
        self.variation = variation
        self.move_list = moves.split() if moves else []
        
    def matches(self, board: chess.Board) -> bool:
        """
        Check if the board position matches this opening
        
        Args:
            board: Chess board to check
            
        Returns:
            True if matches
        """
        # Create temporary board
        temp_board = chess.Board()
        
        # Try to play the opening moves
        for move_uci in self.move_list:
            try:
                move = chess.Move.from_uci(move_uci)
                if move not in temp_board.legal_moves:
                    return False
                temp_board.push(move)
            except:
                return False
                
        # Check if positions match
        return temp_board.fen().split()[0] == board.fen().split()[0]
        
    def __str__(self):
        if self.variation:
            return f"{self.name}: {self.variation} ({self.eco})"
        return f"{self.name} ({self.eco})"


class OpeningBook:
    """Opening book with ECO classification"""
    
    def __init__(self, data_file: Optional[str] = None):
        """
        Initialize opening book
        
        Args:
            data_file: Path to JSON file with opening data
        """
        self.openings: List[Opening] = []
        self.data_file = Path(data_file) if data_file else Path("data/openings.json")
        
        # Load openings
        if self.data_file.exists():
            self.load_from_file()
        else:
            self.load_default_openings()
            
    def load_from_file(self):
        """Load openings from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    opening = Opening(
                        eco=item['eco'],
                        name=item['name'],
                        moves=item['moves'],
                        variation=item.get('variation', '')
                    )
                    self.openings.append(opening)
        except Exception as e:
            print(f"Error loading openings: {e}")
            self.load_default_openings()
            
    def load_default_openings(self):
        """Load default opening repertoire"""
        # Common openings with ECO codes
        default_openings = [
            # Open Games (1.e4 e5)
            ("C20", "King's Pawn Game", "e2e4 e7e5", ""),
            ("C23", "Bishop's Opening", "e2e4 e7e5 f1c4", ""),
            ("C25", "Vienna Game", "e2e4 e7e5 b1c3", ""),
            ("C30", "King's Gambit", "e2e4 e7e5 f2f4", ""),
            ("C33", "King's Gambit Accepted", "e2e4 e7e5 f2f4 e5f4", ""),
            ("C42", "Petrov Defense", "e2e4 e7e5 g1f3 g8f6", ""),
            ("C44", "Scotch Game", "e2e4 e7e5 g1f3 b8c6 d2d4", ""),
            ("C45", "Scotch Game", "e2e4 e7e5 g1f3 b8c6 d2d4 e5d4", ""),
            ("C50", "Italian Game", "e2e4 e7e5 g1f3 b8c6 f1c4", ""),
            ("C53", "Giuoco Piano", "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5", ""),
            ("C54", "Giuoco Piano", "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 c2c3", ""),
            ("C55", "Two Knights Defense", "e2e4 e7e5 g1f3 b8c6 f1c4 g8f6", ""),
            ("C57", "Two Knights Defense: Fried Liver", "e2e4 e7e5 g1f3 b8c6 f1c4 g8f6 f3g5 d7d5 e4d5 f6d5 g5f7", ""),
            ("C60", "Ruy Lopez", "e2e4 e7e5 g1f3 b8c6 f1b5", ""),
            ("C65", "Ruy Lopez: Berlin Defense", "e2e4 e7e5 g1f3 b8c6 f1b5 g8f6", ""),
            ("C78", "Ruy Lopez: Morphy Defense", "e2e4 e7e5 g1f3 b8c6 f1b5 a7a6 b5a4 g8f6 e1g1 f8e7", ""),
            ("C89", "Ruy Lopez: Marshall Attack", "e2e4 e7e5 g1f3 b8c6 f1b5 a7a6 b5a4 g8f6 e1g1 f8e7 f1e1 b7b5 a4b3 e8g8 c2c3 d7d5", ""),
            
            # Semi-Open Games
            ("B00", "King's Pawn Opening", "e2e4", ""),
            ("B01", "Scandinavian Defense", "e2e4 d7d5", ""),
            ("B02", "Alekhine Defense", "e2e4 g8f6", ""),
            ("B06", "Modern Defense", "e2e4 g7g6", ""),
            ("B10", "Caro-Kann Defense", "e2e4 c7c6", ""),
            ("B12", "Caro-Kann: Advance Variation", "e2e4 c7c6 d2d4 d7d5 e4e5", ""),
            ("B20", "Sicilian Defense", "e2e4 c7c5", ""),
            ("B22", "Sicilian: Alapin", "e2e4 c7c5 c2c3", ""),
            ("B23", "Sicilian: Closed", "e2e4 c7c5 b1c3", ""),
            ("B30", "Sicilian: Old Sicilian", "e2e4 c7c5 g1f3 b8c6", ""),
            ("B33", "Sicilian: Sveshnikov", "e2e4 c7c5 g1f3 b8c6 d2d4 c5d4 f3d4 g8f6 b1c3 e7e5", ""),
            ("B40", "Sicilian: French Variation", "e2e4 c7c5 g1f3 e7e6", ""),
            ("B50", "Sicilian Defense", "e2e4 c7c5 g1f3 d7d6", ""),
            ("B70", "Sicilian: Dragon", "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 g7g6", ""),
            ("B80", "Sicilian: Scheveningen", "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 e7e6", ""),
            ("B90", "Sicilian: Najdorf", "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 a7a6", ""),
            
            # Closed Games (1.d4)
            ("D00", "Queen's Pawn Game", "d2d4", ""),
            ("D02", "Queen's Pawn Game", "d2d4 d7d5 g1f3 g8f6", ""),
            ("D04", "Queen's Pawn: Colle System", "d2d4 d7d5 g1f3 g8f6 e2e3", ""),
            ("D05", "Queen's Pawn: Colle System", "d2d4 d7d5 g1f3 g8f6 e2e3 e7e6", ""),
            ("D10", "Slav Defense", "d2d4 d7d5 c2c4 c7c6", ""),
            ("D20", "Queen's Gambit Accepted", "d2d4 d7d5 c2c4 d5c4", ""),
            ("D30", "Queen's Gambit Declined", "d2d4 d7d5 c2c4 e7e6", ""),
            ("D35", "QGD: Exchange Variation", "d2d4 d7d5 c2c4 e7e6 b1c3 g8f6 c4d5", ""),
            ("D37", "QGD: Classical", "d2d4 d7d5 c2c4 e7e6 g1f3 g8f6 b1c3 f8e7", ""),
            ("D43", "QGD: Semi-Slav", "d2d4 d7d5 c2c4 e7e6 g1f3 g8f6 b1c3 c7c6", ""),
            ("D50", "QGD", "d2d4 d7d5 c2c4 e7e6 b1c3 g8f6 c1g5", ""),
            ("D60", "QGD: Orthodox", "d2d4 d7d5 c2c4 e7e6 g1f3 g8f6 b1c3 f8e7 c1g5 e8g8 e2e3 b8d7", ""),
            ("D85", "Grünfeld Defense", "d2d4 g8f6 c2c4 g7g6 b1c3 d7d5", ""),
            
            # Indian Defenses
            ("E00", "Queen's Pawn: Indian", "d2d4 g8f6", ""),
            ("E10", "Queen's Pawn: Indian", "d2d4 g8f6 c2c4 e7e6", ""),
            ("E15", "Queen's Indian Defense", "d2d4 g8f6 c2c4 e7e6 g1f3 b7b6", ""),
            ("E20", "Nimzo-Indian Defense", "d2d4 g8f6 c2c4 e7e6 b1c3 f8b4", ""),
            ("E60", "King's Indian Defense", "d2d4 g8f6 c2c4 g7g6", ""),
            ("E70", "King's Indian: Normal", "d2d4 g8f6 c2c4 g7g6 b1c3 f8g7", ""),
            ("E73", "King's Indian: Averbakh", "d2d4 g8f6 c2c4 g7g6 b1c3 f8g7 e2e4 d7d6 c1e3", ""),
            ("E90", "King's Indian: Classical", "d2d4 g8f6 c2c4 g7g6 b1c3 f8g7 e2e4 d7d6 g1f3 e8g8", ""),
            ("E97", "King's Indian: Mar del Plata", "d2d4 g8f6 c2c4 g7g6 b1c3 f8g7 e2e4 d7d6 g1f3 e8g8 f1e2 e7e5 e1g1 b8c6", ""),
            
            # Flank Openings
            ("A00", "Uncommon Opening", "", ""),
            ("A04", "Réti Opening", "g1f3", ""),
            ("A06", "Réti: King's Indian Attack", "g1f3 d7d5 g2g3", ""),
            ("A10", "English Opening", "c2c4", ""),
            ("A13", "English: Agincourt", "c2c4 e7e6", ""),
            ("A15", "English: Anglo-Indian", "c2c4 g8f6", ""),
            ("A30", "English: Symmetrical", "c2c4 c7c5", ""),
            ("A40", "Queen's Pawn", "d2d4 e7e5", ""),
            ("A45", "Queen's Pawn Game", "d2d4 g8f6", ""),
            ("A80", "Dutch Defense", "d2d4 f7f5", ""),
            ("A90", "Dutch: Stonewall", "d2d4 f7f5 c2c4 g8f6 g2g3 e7e6 f1g2 d7d5", ""),
        ]
        
        for eco, name, moves, variation in default_openings:
            self.openings.append(Opening(eco, name, moves, variation))
            
    def recognize_opening(self, board: chess.Board) -> Optional[Opening]:
        """
        Recognize the opening from the current board position
        
        Args:
            board: Chess board
            
        Returns:
            Opening object or None if not recognized
        """
        # Get move history
        move_list = []
        temp_board = chess.Board()
        
        for move in board.move_stack:
            move_list.append(move.uci())
            
        # Find longest matching opening
        best_match = None
        best_length = 0
        
        for opening in self.openings:
            if len(opening.move_list) > best_length:
                # Check if opening moves match
                if len(move_list) >= len(opening.move_list):
                    matches = True
                    for i, move_uci in enumerate(opening.move_list):
                        if i >= len(move_list) or move_list[i] != move_uci:
                            matches = False
                            break
                    
                    if matches:
                        best_match = opening
                        best_length = len(opening.move_list)
                        
        return best_match
        
    def get_opening_stats(self, games: List[Dict]) -> Dict[str, Dict]:
        """
        Analyze opening statistics from a list of games
        
        Args:
            games: List of game dictionaries
            
        Returns:
            Dictionary of opening statistics
        """
        stats = {}
        
        for game in games:
            # TODO: Recognize opening from game
            # For now, return empty stats
            pass
            
        return stats
        
    def get_all_eco_codes(self) -> List[str]:
        """Get list of all ECO codes"""
        return sorted(list(set(opening.eco for opening in self.openings)))
        
    def get_openings_by_eco(self, eco: str) -> List[Opening]:
        """Get all openings with a specific ECO code"""
        return [op for op in self.openings if op.eco == eco]
        
    def search_openings(self, query: str) -> List[Opening]:
        """
        Search openings by name
        
        Args:
            query: Search query
            
        Returns:
            List of matching openings
        """
        query = query.lower()
        return [op for op in self.openings 
                if query in op.name.lower() or query in op.eco.lower()]

