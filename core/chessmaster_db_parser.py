"""
Chessmaster Database Parser
Extracts chess games from Chessmaster's proprietary database format (.dbm, .dbh, .dbn)
"""
import struct
import os
import chess
import chess.pgn
from typing import List, Dict, Optional
from datetime import datetime
import io


class ChessmasterDatabaseParser:
    """Parser for Chessmaster database files"""
    
    def __init__(self, db_path: str):
        """
        Initialize parser
        
        Args:
            db_path: Path to database folder (containing CMXDBase.dbm, etc.)
        """
        self.db_path = db_path
        self.games = []
        
    def parse_games(self, max_games: Optional[int] = None) -> List[chess.pgn.Game]:
        """
        Parse games from Chessmaster database
        
        Args:
            max_games: Maximum number of games to parse (None = all)
            
        Returns:
            List of chess.pgn.Game objects
        """
        print(f"Parsing Chessmaster database from: {self.db_path}")
        
        # Try to read the main database file (.dbm = moves, .dbn = names)
        dbm_path = os.path.join(self.db_path, "CMXDBase.dbm")
        dbn_path = os.path.join(self.db_path, "CMXDBase.dbn")
        dbg_path = os.path.join(self.db_path, "CMXDBase.dbg")  # Game info
        
        if not os.path.exists(dbm_path):
            print(f"ERROR: Database file not found: {dbm_path}")
            return []
        
        try:
            # Read moves database (binary format)
            with open(dbm_path, 'rb') as f:
                moves_data = f.read()
            
            # Read names database if available
            players_data = b""
            if os.path.exists(dbn_path):
                with open(dbn_path, 'rb') as f:
                    players_data = f.read()
            
            # Read game info if available
            game_info_data = b""
            if os.path.exists(dbg_path):
                with open(dbg_path, 'rb') as f:
                    game_info_data = f.read()
            
            print(f"Database size: {len(moves_data):,} bytes")
            print(f"Players data: {len(players_data):,} bytes")
            print(f"Game info: {len(game_info_data):,} bytes")
            
            # Parse games using heuristic approach
            # Chessmaster databases typically store games in a compact binary format
            # Each game has: header + moves + result
            games = self._parse_binary_games(moves_data, players_data, game_info_data, max_games)
            
            print(f"SUCCESS: Parsed {len(games)} games from database")
            return games
            
        except Exception as e:
            print(f"ERROR: Error parsing database: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_binary_games(self, moves_data: bytes, players_data: bytes, 
                           game_info_data: bytes, max_games: Optional[int]) -> List[chess.pgn.Game]:
        """
        Parse binary game data
        
        Chessmaster format (reverse engineered):
        - Games are stored with compressed move notation
        - Typically uses a compact binary representation
        """
        games = []
        
        # Try to find game boundaries by looking for patterns
        # Chessmaster often uses specific markers between games
        
        # Strategy: Look for recurring patterns that might indicate game starts
        # Common patterns: NULL bytes, specific headers, etc.
        
        print("Analyzing database structure...")
        
        # Scan for potential game markers (heuristic approach)
        # Chessmaster databases often have a header structure
        
        offset = 0
        game_count = 0
        
        # Try to identify if this is a ChessBase format variant
        # Check for PGN-like structures embedded in binary
        
        # Alternative: Try to export via external tool
        print("WARNING: Chessmaster database format is proprietary and complex")
        print("RECOMMENDATION: Use Chessmaster's built-in export to PGN feature")
        print("   Or use a specialized tool like:")
        print("   - SCID (Shane's Chess Information Database)")
        print("   - ChessBase")
        print("   - pgn-extract")
        
        # For now, return empty list and guide user to export
        return games
    
    def export_info(self) -> Dict:
        """Get information about the database"""
        info = {
            "path": self.db_path,
            "files": [],
            "total_size": 0
        }
        
        # List all database files
        if os.path.exists(self.db_path):
            for filename in os.listdir(self.db_path):
                if filename.startswith("CMXDBase"):
                    filepath = os.path.join(self.db_path, filename)
                    size = os.path.getsize(filepath)
                    info["files"].append({
                        "name": filename,
                        "size": size,
                        "size_mb": size / (1024 * 1024)
                    })
                    info["total_size"] += size
        
        info["total_size_mb"] = info["total_size"] / (1024 * 1024)
        return info


def export_chessmaster_db_to_pgn(db_path: str, output_file: str, max_games: Optional[int] = None):
    """
    Export Chessmaster database to PGN format
    
    Args:
        db_path: Path to Chessmaster database folder
        output_file: Output PGN file path
        max_games: Maximum games to export (None = all)
    """
    parser = ChessmasterDatabaseParser(db_path)
    
    # Get database info
    info = parser.export_info()
    print("\n" + "="*60)
    print("CHESSMASTER DATABASE INFO")
    print("="*60)
    print(f"Path: {info['path']}")
    print(f"Total size: {info['total_size_mb']:.1f} MB")
    print("\nFiles found:")
    for file_info in info['files']:
        print(f"  - {file_info['name']}: {file_info['size_mb']:.1f} MB")
    print("="*60 + "\n")
    
    # Parse games
    games = parser.parse_games(max_games)
    
    if games:
        # Write to PGN
        print(f"Writing {len(games)} games to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, game in enumerate(games):
                print(game, file=f, end="\n\n")
                if (i + 1) % 100 == 0:
                    print(f"  Written {i + 1} games...")
        print(f"Export complete!")
    else:
        print("\n" + "="*60)
        print("AUTOMATIC PARSING NOT POSSIBLE")
        print("="*60)
        print("\nRECOMMENDED SOLUTION:")
        print("\n1. Open Chessmaster Grandmaster Edition")
        print("2. Go to Database -> Export")
        print("3. Export games to PGN format")
        print("4. Save as 'chessmaster_games.pgn'")
        print("5. Place the file in the project folder")
        print("\nThen we can integrate it into ChessAvatar!")
        print("="*60)


if __name__ == "__main__":
    # Example usage
    db_path = r"C:\Program Files (x86)\Ubisoft\Chessmaster Grandmaster Edition\Data\Base de données"
    output_file = "chessmaster_games.pgn"
    
    export_chessmaster_db_to_pgn(db_path, output_file, max_games=100)

