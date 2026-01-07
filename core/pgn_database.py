"""
PGN Database Manager
Handles importing and querying chess games from PGN databases
"""
import chess.pgn
import os
import json
from typing import List, Dict, Optional
from datetime import datetime


class PGNDatabaseManager:
    """Manager for PGN game databases"""
    
    def __init__(self, db_folder: str = "database"):
        """
        Initialize database manager
        
        Args:
            db_folder: Folder to store database files
        """
        self.db_folder = db_folder
        os.makedirs(db_folder, exist_ok=True)
        
        self.games_index = {}  # In-memory index: player -> game IDs
        self.games_file = None  # PGN file handle
        self.index_file = os.path.join(db_folder, "games_index.json")
        
        self._load_index()
    
    def import_pgn(self, pgn_path: str, max_games: Optional[int] = None) -> int:
        """
        Import games from PGN file
        
        Args:
            pgn_path: Path to PGN file
            max_games: Maximum games to import (None = all)
            
        Returns:
            Number of games imported
        """
        print(f"Importing games from: {pgn_path}")
        
        if not os.path.exists(pgn_path):
            print(f"ERROR: File not found: {pgn_path}")
            return 0
        
        # Copy PGN to database folder
        db_pgn_path = os.path.join(self.db_folder, "games.pgn")
        
        imported = 0
        try:
            with open(pgn_path, 'r', encoding='utf-8', errors='ignore') as src:
                with open(db_pgn_path, 'w', encoding='utf-8') as dst:
                    while True:
                        game = chess.pgn.read_game(src)
                        if game is None:
                            break
                        
                        # Write game to database
                        print(game, file=dst, end="\n\n")
                        
                        # Index game
                        self._index_game(game, imported)
                        
                        imported += 1
                        if imported % 1000 == 0:
                            print(f"  Imported {imported} games...")
                        
                        if max_games and imported >= max_games:
                            break
            
            # Save index
            self._save_index()
            print(f"SUCCESS: Imported {imported} games!")
            return imported
            
        except Exception as e:
            print(f"ERROR: Failed to import PGN: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def _index_game(self, game: chess.pgn.Game, game_id: int):
        """Add game to index"""
        headers = game.headers
        
        # Index by white player
        white = headers.get("White", "Unknown")
        if white not in self.games_index:
            self.games_index[white] = []
        self.games_index[white].append(game_id)
        
        # Index by black player
        black = headers.get("Black", "Unknown")
        if black not in self.games_index:
            self.games_index[black] = []
        self.games_index[black].append(game_id)
        
        # Index by opening (ECO code)
        eco = headers.get("ECO", "")
        if eco:
            key = f"ECO_{eco}"
            if key not in self.games_index:
                self.games_index[key] = []
            self.games_index[key].append(game_id)
    
    def search_by_player(self, player_name: str, max_results: int = 10) -> List[chess.pgn.Game]:
        """
        Search games by player name
        
        Args:
            player_name: Player name (partial match)
            max_results: Maximum results to return
            
        Returns:
            List of games
        """
        # Find matching player names
        matching_players = [p for p in self.games_index.keys() 
                           if player_name.lower() in p.lower() and not p.startswith("ECO_")]
        
        if not matching_players:
            return []
        
        # Get game IDs
        game_ids = []
        for player in matching_players:
            game_ids.extend(self.games_index[player][:max_results])
        
        # Load games
        return self._load_games_by_ids(game_ids[:max_results])
    
    def search_by_opening(self, eco_code: str, max_results: int = 10) -> List[chess.pgn.Game]:
        """
        Search games by ECO opening code
        
        Args:
            eco_code: ECO code (e.g., "C50", "E70")
            max_results: Maximum results
            
        Returns:
            List of games
        """
        key = f"ECO_{eco_code}"
        if key not in self.games_index:
            return []
        
        game_ids = self.games_index[key][:max_results]
        return self._load_games_by_ids(game_ids)
    
    def _load_games_by_ids(self, game_ids: List[int]) -> List[chess.pgn.Game]:
        """Load specific games from database"""
        db_pgn_path = os.path.join(self.db_folder, "games.pgn")
        
        if not os.path.exists(db_pgn_path):
            return []
        
        games = []
        with open(db_pgn_path, 'r', encoding='utf-8', errors='ignore') as f:
            current_id = 0
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                
                if current_id in game_ids:
                    games.append(game)
                
                current_id += 1
        
        return games
    
    def _load_index(self):
        """Load index from disk"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.games_index = json.load(f)
            except:
                self.games_index = {}
    
    def _save_index(self):
        """Save index to disk"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.games_index, f, indent=2)
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        db_pgn_path = os.path.join(self.db_folder, "games.pgn")
        
        stats = {
            "total_games": 0,
            "total_players": 0,
            "total_openings": 0,
            "database_size_mb": 0.0
        }
        
        if os.path.exists(db_pgn_path):
            stats["database_size_mb"] = os.path.getsize(db_pgn_path) / (1024 * 1024)
        
        # Count from index
        players = [k for k in self.games_index.keys() if not k.startswith("ECO_")]
        openings = [k for k in self.games_index.keys() if k.startswith("ECO_")]
        
        stats["total_players"] = len(players)
        stats["total_openings"] = len(openings)
        
        # Count total games (from first player's games)
        if players:
            stats["total_games"] = len(self.games_index[players[0]])
        
        return stats


# Global instance
_pgn_db_manager = None

def get_pgn_database_manager() -> PGNDatabaseManager:
    """Get global PGN database manager instance"""
    global _pgn_db_manager
    if _pgn_db_manager is None:
        _pgn_db_manager = PGNDatabaseManager()
    return _pgn_db_manager


if __name__ == "__main__":
    # Test
    manager = PGNDatabaseManager()
    stats = manager.get_stats()
    print("Database stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

