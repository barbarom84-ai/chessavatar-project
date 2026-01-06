"""
Style Analyzer for chess games
Analyzes player's style, openings, and performance
"""
import chess
import chess.pgn
from io import StringIO
from typing import List, Dict, Tuple
from collections import Counter, defaultdict
from dataclasses import dataclass
from core.api_service import GameData


@dataclass
class PlayerStyle:
    """Data structure for player's chess style"""
    username: str
    platform: str
    total_games: int
    win_rate: float
    draw_rate: float
    loss_rate: float
    average_elo: int
    
    # Opening statistics
    top_openings_white: List[Tuple[str, int]]  # (opening, count)
    top_openings_black: List[Tuple[str, int]]
    
    # Playing style metrics
    average_game_length: float
    aggressive_score: float  # 0-100
    tactical_score: float    # 0-100
    positional_score: float  # 0-100
    
    # Performance by color
    white_win_rate: float
    black_win_rate: float
    
    # Time control preference
    preferred_time_control: str
    
    # Estimated skill level (for Stockfish)
    estimated_skill_level: int  # 0-20


class StyleAnalyzer:
    """Analyzer for player's chess style"""
    
    def __init__(self):
        self.games: List[GameData] = []
        
    def analyze_games(self, games: List[GameData], username: str, platform: str) -> PlayerStyle:
        """
        Analyze games and extract player style
        
        Args:
            games: List of GameData objects
            username: Player's username
            platform: Platform (Lichess or Chess.com)
            
        Returns:
            PlayerStyle object
        """
        self.games = games
        
        if not games:
            return self._create_default_style(username, platform)
            
        # Basic statistics
        total_games = len(games)
        wins = 0
        draws = 0
        losses = 0
        elo_sum = 0
        elo_count = 0
        
        # Color-specific stats
        games_as_white = 0
        wins_as_white = 0
        games_as_black = 0
        wins_as_black = 0
        
        # Opening statistics
        openings_white = []
        openings_black = []
        
        # Game length and style
        game_lengths = []
        
        # Time control
        time_controls = []
        
        for game in games:
            is_white = game.white.lower() == username.lower()
            is_black = game.black.lower() == username.lower()
            
            if not (is_white or is_black):
                continue
                
            # Result analysis
            if game.result == '1-0':
                if is_white:
                    wins += 1
                    wins_as_white += 1
                else:
                    losses += 1
            elif game.result == '0-1':
                if is_black:
                    wins += 1
                    wins_as_black += 1
                else:
                    losses += 1
            elif game.result == '1/2-1/2':
                draws += 1
                
            # Color counting
            if is_white:
                games_as_white += 1
                if game.opening != 'Unknown':
                    openings_white.append(game.opening)
            else:
                games_as_black += 1
                if game.opening != 'Unknown':
                    openings_black.append(game.opening)
                    
            # Elo
            if is_white and game.white_elo > 0:
                elo_sum += game.white_elo
                elo_count += 1
            elif is_black and game.black_elo > 0:
                elo_sum += game.black_elo
                elo_count += 1
                
            # Game length
            moves = game.moves.split()
            if moves:
                game_lengths.append(len(moves))
                
            # Time control
            if game.time_control != 'Unknown':
                time_controls.append(game.time_control)
                
        # Calculate rates
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        draw_rate = (draws / total_games * 100) if total_games > 0 else 0
        loss_rate = (losses / total_games * 100) if total_games > 0 else 0
        
        white_win_rate = (wins_as_white / games_as_white * 100) if games_as_white > 0 else 0
        black_win_rate = (wins_as_black / games_as_black * 100) if games_as_black > 0 else 0
        
        average_elo = int(elo_sum / elo_count) if elo_count > 0 else 1500
        
        # Top openings
        opening_counter_white = Counter(openings_white)
        opening_counter_black = Counter(openings_black)
        
        top_openings_white = opening_counter_white.most_common(5)
        top_openings_black = opening_counter_black.most_common(5)
        
        # Average game length
        average_game_length = sum(game_lengths) / len(game_lengths) if game_lengths else 40
        
        # Playing style scores
        aggressive_score = self._calculate_aggressive_score(average_game_length, win_rate)
        tactical_score = self._calculate_tactical_score(average_game_length, openings_white, openings_black)
        positional_score = 100 - aggressive_score  # Simplified
        
        # Preferred time control
        time_control_counter = Counter(time_controls)
        preferred_time_control = time_control_counter.most_common(1)[0][0] if time_control_counter else 'blitz'
        
        # Estimate skill level for Stockfish (0-20)
        estimated_skill_level = self._estimate_skill_level(average_elo, win_rate)
        
        return PlayerStyle(
            username=username,
            platform=platform,
            total_games=total_games,
            win_rate=round(win_rate, 1),
            draw_rate=round(draw_rate, 1),
            loss_rate=round(loss_rate, 1),
            average_elo=average_elo,
            top_openings_white=top_openings_white,
            top_openings_black=top_openings_black,
            average_game_length=round(average_game_length, 1),
            aggressive_score=round(aggressive_score, 1),
            tactical_score=round(tactical_score, 1),
            positional_score=round(positional_score, 1),
            white_win_rate=round(white_win_rate, 1),
            black_win_rate=round(black_win_rate, 1),
            preferred_time_control=preferred_time_control,
            estimated_skill_level=estimated_skill_level
        )
        
    def _calculate_aggressive_score(self, avg_game_length: float, win_rate: float) -> float:
        """
        Calculate aggressiveness score based on game length and win rate
        Shorter games with high win rate = more aggressive
        """
        # Normalize game length (20-60 moves typical)
        length_score = max(0, min(100, (60 - avg_game_length) * 2))
        
        # Combine with win rate
        aggressive = (length_score * 0.7) + (win_rate * 0.3)
        
        return max(0, min(100, aggressive))
        
    def _calculate_tactical_score(self, avg_game_length: float, openings_white: List[str], openings_black: List[str]) -> float:
        """
        Calculate tactical vs positional play score
        Sharp openings and shorter games = more tactical
        """
        # Tactical openings (simplified list)
        tactical_openings = [
            'sicilian', 'dragon', 'najdorf', 'king', 'gambit', 
            'attack', 'defense', 'counter', 'benoni', 'dutch'
        ]
        
        tactical_count = 0
        total_count = 0
        
        for opening in openings_white + openings_black:
            opening_lower = opening.lower()
            total_count += 1
            if any(tactical in opening_lower for tactical in tactical_openings):
                tactical_count += 1
                
        opening_score = (tactical_count / total_count * 100) if total_count > 0 else 50
        
        # Shorter games tend to be more tactical
        length_score = max(0, min(100, (60 - avg_game_length) * 1.5))
        
        tactical = (opening_score * 0.6) + (length_score * 0.4)
        
        return max(0, min(100, tactical))
        
    def _estimate_skill_level(self, elo: int, win_rate: float) -> int:
        """
        Estimate Stockfish skill level (0-20) based on player's Elo
        
        Mapping (approximate):
        1000 Elo = Skill 0-2
        1200 Elo = Skill 3-5
        1400 Elo = Skill 6-8
        1600 Elo = Skill 9-11
        1800 Elo = Skill 12-14
        2000 Elo = Skill 15-16
        2200 Elo = Skill 17-18
        2400+ Elo = Skill 19-20
        """
        if elo < 1000:
            base_skill = 0
        elif elo < 1200:
            base_skill = 3
        elif elo < 1400:
            base_skill = 6
        elif elo < 1600:
            base_skill = 9
        elif elo < 1800:
            base_skill = 12
        elif elo < 2000:
            base_skill = 15
        elif elo < 2200:
            base_skill = 17
        elif elo < 2400:
            base_skill = 19
        else:
            base_skill = 20
            
        # Adjust based on win rate
        if win_rate > 60:
            base_skill = min(20, base_skill + 1)
        elif win_rate < 40:
            base_skill = max(0, base_skill - 1)
            
        return base_skill
        
    def _create_default_style(self, username: str, platform: str) -> PlayerStyle:
        """Create default style when no games are available"""
        return PlayerStyle(
            username=username,
            platform=platform,
            total_games=0,
            win_rate=0.0,
            draw_rate=0.0,
            loss_rate=0.0,
            average_elo=1500,
            top_openings_white=[],
            top_openings_black=[],
            average_game_length=40.0,
            aggressive_score=50.0,
            tactical_score=50.0,
            positional_score=50.0,
            white_win_rate=0.0,
            black_win_rate=0.0,
            preferred_time_control='blitz',
            estimated_skill_level=10
        )
        
    def generate_style_report(self, style: PlayerStyle) -> str:
        """Generate a human-readable style report"""
        report = f"""
╔══════════════════════════════════════════════════════════╗
║           Profil de Joueur - {style.username}
╚══════════════════════════════════════════════════════════╝

📊 STATISTIQUES GÉNÉRALES
  Plateforme:        {style.platform}
  Parties jouées:    {style.total_games}
  Elo moyen:         {style.average_elo}
  
  Victoires:         {style.win_rate}%
  Nulles:            {style.draw_rate}%
  Défaites:          {style.loss_rate}%

🎨 STYLE DE JEU
  Agressivité:       {style.aggressive_score}/100
  Tactique:          {style.tactical_score}/100
  Positionnel:       {style.positional_score}/100
  
  Longueur moyenne:  {style.average_game_length} coups

♟️ PERFORMANCE PAR COULEUR
  Blancs:            {style.white_win_rate}% victoires
  Noirs:             {style.black_win_rate}% victoires

📖 OUVERTURES FAVORITES (Blancs)
"""
        
        for i, (opening, count) in enumerate(style.top_openings_white[:3], 1):
            percentage = (count / style.total_games * 100) if style.total_games > 0 else 0
            report += f"  {i}. {opening}: {count} parties ({percentage:.1f}%)\n"
            
        report += "\n📖 OUVERTURES FAVORITES (Noirs)\n"
        
        for i, (opening, count) in enumerate(style.top_openings_black[:3], 1):
            percentage = (count / style.total_games * 100) if style.total_games > 0 else 0
            report += f"  {i}. {opening}: {count} parties ({percentage:.1f}%)\n"
            
        report += f"""
⚙️ CONFIGURATION MOTEUR
  Niveau Stockfish estimé: {style.estimated_skill_level}/20
  Cadence préférée: {style.preferred_time_control}

════════════════════════════════════════════════════════════
"""
        
        return report

