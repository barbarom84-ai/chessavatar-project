"""
API Service for fetching games from Lichess and Chess.com
"""
import requests
import chess.pgn
from io import StringIO
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GameData:
    """Data structure for a chess game"""
    white: str
    black: str
    result: str
    pgn: str
    opening: str
    time_control: str
    date: str
    white_elo: int
    black_elo: int
    moves: str


class APIService:
    """Service for fetching games from chess platforms"""
    
    def __init__(self):
        self.lichess_base_url = "https://lichess.org/api"
        self.chesscom_base_url = "https://api.chess.com/pub"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ChessAvatar/1.0'
        })
        
    def fetch_lichess_games(self, username: str, max_games: int = 100) -> List[GameData]:
        """
        Fetch recent games from Lichess
        
        Args:
            username: Lichess username
            max_games: Maximum number of games to fetch
            
        Returns:
            List of GameData objects
        """
        games = []
        
        try:
            # Lichess API endpoint for user games
            url = f"{self.lichess_base_url}/games/user/{username}"
            params = {
                'max': max_games,
                'rated': 'true',
                'perfType': 'blitz,rapid,classical',
                'opening': 'true',
                'moves': 'true',
                'pgnInJson': 'false',
                'tags': 'true',
                'clocks': 'false',
                'evals': 'false'
            }
            
            # Stream the response
            response = self.session.get(url, params=params, stream=True, timeout=30)
            response.raise_for_status()
            
            # Parse NDJSON (newline-delimited JSON)
            pgn_text = ""
            for line in response.iter_lines():
                if line:
                    pgn_text += line.decode('utf-8') + "\n\n"
                    
            # Parse PGN
            games = self._parse_pgn_text(pgn_text)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Lichess games: {e}")
        except Exception as e:
            print(f"Error parsing Lichess games: {e}")
            
        return games[:max_games]
        
    def fetch_chesscom_games(self, username: str, max_games: int = 100) -> List[GameData]:
        """
        Fetch recent games from Chess.com
        
        Args:
            username: Chess.com username
            max_games: Maximum number of games to fetch
            
        Returns:
            List of GameData objects
        """
        games = []
        
        try:
            # Get player's game archives
            archives_url = f"{self.chesscom_base_url}/player/{username}/games/archives"
            archives_response = self.session.get(archives_url, timeout=30)
            archives_response.raise_for_status()
            
            archives = archives_response.json().get('archives', [])
            
            # Fetch games from most recent archives
            for archive_url in reversed(archives):
                if len(games) >= max_games:
                    break
                    
                try:
                    archive_response = self.session.get(archive_url, timeout=30)
                    archive_response.raise_for_status()
                    archive_data = archive_response.json()
                    
                    for game in archive_data.get('games', []):
                        if len(games) >= max_games:
                            break
                            
                        # Extract game data
                        game_data = self._parse_chesscom_game(game, username)
                        if game_data:
                            games.append(game_data)
                            
                except Exception as e:
                    print(f"Error fetching archive {archive_url}: {e}")
                    continue
                    
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Chess.com games: {e}")
        except Exception as e:
            print(f"Error parsing Chess.com games: {e}")
            
        return games[:max_games]
        
    def _parse_pgn_text(self, pgn_text: str) -> List[GameData]:
        """Parse PGN text into GameData objects"""
        games = []
        pgn_io = StringIO(pgn_text)
        
        while True:
            try:
                game = chess.pgn.read_game(pgn_io)
                if game is None:
                    break
                    
                headers = game.headers
                
                # Extract moves
                moves = []
                node = game
                while node.variations:
                    node = node.variations[0]
                    moves.append(node.san())
                    
                game_data = GameData(
                    white=headers.get('White', 'Unknown'),
                    black=headers.get('Black', 'Unknown'),
                    result=headers.get('Result', '*'),
                    pgn=str(game),
                    opening=headers.get('Opening', 'Unknown'),
                    time_control=headers.get('TimeControl', 'Unknown'),
                    date=headers.get('Date', 'Unknown'),
                    white_elo=int(headers.get('WhiteElo', 0)),
                    black_elo=int(headers.get('BlackElo', 0)),
                    moves=' '.join(moves)
                )
                games.append(game_data)
                
            except Exception as e:
                print(f"Error parsing game: {e}")
                continue
                
        return games
        
    def _parse_chesscom_game(self, game: Dict, username: str) -> Optional[GameData]:
        """Parse Chess.com game JSON into GameData"""
        try:
            # Get PGN
            pgn_text = game.get('pgn', '')
            if not pgn_text:
                return None
                
            # Parse PGN
            pgn_io = StringIO(pgn_text)
            parsed_game = chess.pgn.read_game(pgn_io)
            if not parsed_game:
                return None
                
            headers = parsed_game.headers
            
            # Extract moves
            moves = []
            node = parsed_game
            while node.variations:
                node = node.variations[0]
                moves.append(node.san())
                
            # Determine result from user's perspective
            white = headers.get('White', '')
            black = headers.get('Black', '')
            result = headers.get('Result', '*')
            
            game_data = GameData(
                white=white,
                black=black,
                result=result,
                pgn=pgn_text,
                opening=headers.get('ECOUrl', 'Unknown').split('/')[-1] if 'ECOUrl' in headers else 'Unknown',
                time_control=game.get('time_class', 'Unknown'),
                date=headers.get('Date', 'Unknown'),
                white_elo=int(headers.get('WhiteElo', 0)),
                black_elo=int(headers.get('BlackElo', 0)),
                moves=' '.join(moves)
            )
            
            return game_data
            
        except Exception as e:
            print(f"Error parsing Chess.com game: {e}")
            return None
            
    def verify_username(self, platform: str, username: str) -> bool:
        """
        Verify if a username exists on the platform
        
        Args:
            platform: 'lichess' or 'chesscom'
            username: Username to verify
            
        Returns:
            True if username exists
        """
        try:
            if platform == 'lichess':
                url = f"{self.lichess_base_url}/user/{username}"
                response = self.session.get(url, timeout=10)
                return response.status_code == 200
                
            elif platform == 'chesscom':
                url = f"{self.chesscom_base_url}/player/{username}"
                response = self.session.get(url, timeout=10)
                return response.status_code == 200
                
        except Exception as e:
            print(f"Error verifying username: {e}")
            return False
            
        return False
        
    def get_player_stats(self, platform: str, username: str) -> Optional[Dict]:
        """
        Get player statistics
        
        Args:
            platform: 'lichess' or 'chesscom'
            username: Username
            
        Returns:
            Dictionary with player stats
        """
        try:
            if platform == 'lichess':
                url = f"{self.lichess_base_url}/user/{username}"
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                perfs = data.get('perfs', {})
                return {
                    'username': username,
                    'platform': 'Lichess',
                    'blitz_rating': perfs.get('blitz', {}).get('rating', 0),
                    'rapid_rating': perfs.get('rapid', {}).get('rating', 0),
                    'classical_rating': perfs.get('classical', {}).get('rating', 0),
                    'games_played': data.get('count', {}).get('all', 0)
                }
                
            elif platform == 'chesscom':
                url = f"{self.chesscom_base_url}/player/{username}/stats"
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                chess_blitz = data.get('chess_blitz', {}).get('last', {})
                chess_rapid = data.get('chess_rapid', {}).get('last', {})
                chess_daily = data.get('chess_daily', {}).get('last', {})
                
                return {
                    'username': username,
                    'platform': 'Chess.com',
                    'blitz_rating': chess_blitz.get('rating', 0),
                    'rapid_rating': chess_rapid.get('rating', 0),
                    'classical_rating': chess_daily.get('rating', 0),
                    'games_played': sum([
                        data.get('chess_blitz', {}).get('last', {}).get('games', 0),
                        data.get('chess_rapid', {}).get('last', {}).get('games', 0),
                    ])
                }
                
        except Exception as e:
            print(f"Error fetching player stats: {e}")
            return None

