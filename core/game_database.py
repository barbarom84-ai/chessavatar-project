"""
Game database manager for storing and retrieving chess games
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import chess


class GameDatabase:
    """Manager for game database"""
    
    def __init__(self, db_path: str = "data/games.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Games table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                white_player TEXT NOT NULL,
                black_player TEXT NOT NULL,
                result TEXT,
                moves TEXT NOT NULL,
                pgn TEXT,
                fen_start TEXT,
                fen_end TEXT,
                time_control TEXT,
                game_mode TEXT,
                opening_name TEXT,
                opening_eco TEXT,
                total_moves INTEGER,
                white_elo INTEGER,
                black_elo INTEGER,
                annotations TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Openings table (for custom opening book)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                eco_code TEXT,
                moves TEXT NOT NULL,
                fen TEXT,
                description TEXT,
                popularity INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
    def save_game(self, game_data: Dict) -> int:
        """
        Save a game to database
        
        Args:
            game_data: Dictionary containing game information
            
        Returns:
            ID of saved game
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO games (
                date, white_player, black_player, result, moves, pgn,
                fen_start, fen_end, time_control, game_mode,
                opening_name, opening_eco, total_moves,
                white_elo, black_elo, annotations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            game_data.get('date', datetime.now().isoformat()),
            game_data.get('white_player', 'Unknown'),
            game_data.get('black_player', 'Unknown'),
            game_data.get('result', '*'),
            game_data.get('moves', ''),
            game_data.get('pgn', ''),
            game_data.get('fen_start', chess.STARTING_FEN),
            game_data.get('fen_end', ''),
            game_data.get('time_control', ''),
            game_data.get('game_mode', ''),
            game_data.get('opening_name', ''),
            game_data.get('opening_eco', ''),
            game_data.get('total_moves', 0),
            game_data.get('white_elo', 0),
            game_data.get('black_elo', 0),
            json.dumps(game_data.get('annotations', {}))
        ))
        
        game_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return game_id
        
    def get_game(self, game_id: int) -> Optional[Dict]:
        """Get a game by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM games WHERE id = ?", (game_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        return self._row_to_dict(row)
        
    def get_all_games(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all games with pagination"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM games 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
        
    def search_games(self, 
                     player: Optional[str] = None,
                     opening: Optional[str] = None,
                     result: Optional[str] = None) -> List[Dict]:
        """Search games by criteria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM games WHERE 1=1"
        params = []
        
        if player:
            query += " AND (white_player LIKE ? OR black_player LIKE ?)"
            params.extend([f"%{player}%", f"%{player}%"])
            
        if opening:
            query += " AND (opening_name LIKE ? OR opening_eco LIKE ?)"
            params.extend([f"%{opening}%", f"%{opening}%"])
            
        if result:
            query += " AND result = ?"
            params.append(result)
            
        query += " ORDER BY created_at DESC LIMIT 100"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
        
    def delete_game(self, game_id: int) -> bool:
        """Delete a game"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
        
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM games")
        total_games = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM games WHERE result LIKE '%Blancs%'")
        white_wins = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM games WHERE result LIKE '%Noirs%'")
        black_wins = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM games WHERE result LIKE '%Nulle%'")
        draws = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_games': total_games,
            'white_wins': white_wins,
            'black_wins': black_wins,
            'draws': draws
        }
        
    def save_opening(self, opening_data: Dict) -> int:
        """Save an opening to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO openings (name, eco_code, moves, fen, description, popularity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            opening_data.get('name', ''),
            opening_data.get('eco_code', ''),
            opening_data.get('moves', ''),
            opening_data.get('fen', ''),
            opening_data.get('description', ''),
            opening_data.get('popularity', 0)
        ))
        
        opening_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return opening_id
        
    def get_all_openings(self) -> List[Dict]:
        """Get all openings from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM openings ORDER BY popularity DESC, name ASC")
        rows = cursor.fetchall()
        conn.close()
        
        openings = []
        for row in rows:
            openings.append({
                'id': row[0],
                'name': row[1],
                'eco_code': row[2],
                'moves': row[3],
                'fen': row[4],
                'description': row[5],
                'popularity': row[6]
            })
            
        return openings
        
    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dictionary"""
        return {
            'id': row[0],
            'date': row[1],
            'white_player': row[2],
            'black_player': row[3],
            'result': row[4],
            'moves': row[5],
            'pgn': row[6],
            'fen_start': row[7],
            'fen_end': row[8],
            'time_control': row[9],
            'game_mode': row[10],
            'opening_name': row[11],
            'opening_eco': row[12],
            'total_moves': row[13],
            'white_elo': row[14],
            'black_elo': row[15],
            'annotations': json.loads(row[16]) if row[16] else {},
            'created_at': row[17]
        }


# Singleton instance
_game_db = None

def get_game_database() -> GameDatabase:
    """Get singleton game database instance"""
    global _game_db
    if _game_db is None:
        _game_db = GameDatabase()
    return _game_db

