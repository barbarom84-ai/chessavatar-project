"""
AI Coach - provides hints and advice during gameplay
"""
import chess
from typing import Optional, Dict, List, Tuple
import random


class AICoach:
    """AI Coach that provides hints and strategic advice"""
    
    def __init__(self):
        self.hints_enabled = False
        self.difficulty_level = "intermediate"  # beginner, intermediate, advanced
        
    def enable_hints(self, enabled: bool = True):
        """Enable or disable hints"""
        self.hints_enabled = enabled
        
    def set_difficulty(self, level: str):
        """Set difficulty level for hints"""
        self.difficulty_level = level
        
    def analyze_position(self, board: chess.Board, engine_eval: Optional[Dict] = None) -> Dict:
        """
        Analyze current position and provide advice
        
        Args:
            board: Current board position
            engine_eval: Optional engine evaluation data
            
        Returns:
            Dictionary with analysis and advice
        """
        analysis = {
            'position_type': self._classify_position(board),
            'threats': self._detect_threats(board),
            'opportunities': self._detect_opportunities(board),
            'strategic_advice': [],
            'tactical_hints': [],
            'eval_score': engine_eval.get('score') if engine_eval else None,
            'best_move': engine_eval.get('best_move') if engine_eval else None
        }
        
        # Generate strategic advice
        analysis['strategic_advice'] = self._generate_strategic_advice(board, analysis)
        
        # Generate tactical hints
        analysis['tactical_hints'] = self._generate_tactical_hints(board, analysis)
        
        return analysis
        
    def get_hint(self, board: chess.Board, engine_eval: Optional[Dict] = None) -> str:
        """
        Get a hint for the current position
        
        Args:
            board: Current board position
            engine_eval: Optional engine evaluation
            
        Returns:
            Hint text
        """
        if not self.hints_enabled:
            return "💡 Les conseils du coach sont désactivés"
            
        analysis = self.analyze_position(board, engine_eval)
        
        # Build hint message
        hints = []
        
        # Position evaluation
        if analysis['eval_score'] is not None:
            eval_score = analysis['eval_score']
            if abs(eval_score) < 0.5:
                hints.append("⚖️ Position équilibrée")
            elif eval_score > 2.0:
                hints.append("✅ Blancs ont l'avantage")
            elif eval_score < -2.0:
                hints.append("✅ Noirs ont l'avantage")
                
        # Threats
        if analysis['threats']:
            threat_count = len(analysis['threats'])
            hints.append(f"⚠️ Attention: {threat_count} menace(s) détectée(s)")
            
        # Strategic advice
        if analysis['strategic_advice']:
            hints.extend(analysis['strategic_advice'][:2])  # Top 2 advice
            
        # Tactical hints
        if analysis['tactical_hints']:
            hints.extend(analysis['tactical_hints'][:1])  # Top 1 hint
            
        if not hints:
            hints.append("🤔 Analysez la position calmement")
            
        return "\n".join(hints)
        
    def _classify_position(self, board: chess.Board) -> str:
        """Classify the type of position"""
        # Count pieces
        total_pieces = len(board.piece_map())
        
        if total_pieces <= 10:
            return "endgame"
        elif total_pieces <= 20:
            return "middlegame"
        else:
            return "opening"
            
    def _detect_threats(self, board: chess.Board) -> List[str]:
        """Detect threats in the position"""
        threats = []
        
        # Check if king is in check
        if board.is_check():
            threats.append("Roi en échec!")
            
        # Check for attacked pieces
        player = board.turn
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == player:
                # Check if piece is attacked
                attackers = board.attackers(not player, square)
                defenders = board.attackers(player, square)
                
                if len(attackers) > len(defenders):
                    piece_name = self._get_piece_name(piece.piece_type)
                    threats.append(f"{piece_name} en danger")
                    
        return threats
        
    def _detect_opportunities(self, board: chess.Board) -> List[str]:
        """Detect tactical opportunities"""
        opportunities = []
        
        # Check for available captures
        for move in board.legal_moves:
            if board.is_capture(move):
                captured = board.piece_at(move.to_square)
                if captured:
                    piece_name = self._get_piece_name(captured.piece_type)
                    opportunities.append(f"Capture possible: {piece_name}")
                    
        # Check for checks
        for move in board.legal_moves:
            board.push(move)
            if board.is_check():
                opportunities.append("Échec possible")
            board.pop()
            
        return opportunities[:3]  # Limit to top 3
        
    def _generate_strategic_advice(self, board: chess.Board, analysis: Dict) -> List[str]:
        """Generate strategic advice"""
        advice = []
        position_type = analysis['position_type']
        
        if position_type == "opening":
            advice.extend([
                "♟️ Contrôlez le centre",
                "🏰 Développez vos pièces",
                "👑 Roquezpour la sécurité du roi"
            ])
        elif position_type == "middlegame":
            advice.extend([
                "🎯 Cherchez les faiblesses adverses",
                "⚔️ Coordonnez vos pièces",
                "🛡️ Protégez vos points faibles"
            ])
        elif position_type == "endgame":
            advice.extend([
                "👑 Activez votre roi",
                "♟️ Poussez vos pions passés",
                "🎯 Visez la promotion"
            ])
            
        return advice
        
    def _generate_tactical_hints(self, board: chess.Board, analysis: Dict) -> List[str]:
        """Generate tactical hints"""
        hints = []
        
        # Check for checks available
        has_check = False
        for move in board.legal_moves:
            board.push(move)
            if board.is_check():
                has_check = True
            board.pop()
            if has_check:
                break
                
        if has_check:
            hints.append("💡 Un échec est possible")
            
        # Check for captures
        captures = [m for m in board.legal_moves if board.is_capture(m)]
        if len(captures) > 3:
            hints.append("🎯 Plusieurs captures disponibles")
            
        return hints
        
    def _get_piece_name(self, piece_type: int) -> str:
        """Get French name for piece type"""
        names = {
            chess.PAWN: "Pion",
            chess.KNIGHT: "Cavalier",
            chess.BISHOP: "Fou",
            chess.ROOK: "Tour",
            chess.QUEEN: "Dame",
            chess.KING: "Roi"
        }
        return names.get(piece_type, "Pièce")


# Singleton instance
_ai_coach = None

def get_ai_coach() -> AICoach:
    """Get singleton AI coach instance"""
    global _ai_coach
    if _ai_coach is None:
        _ai_coach = AICoach()
    return _ai_coach

