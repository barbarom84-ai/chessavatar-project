"""
Move annotator - analyzes chess moves and assigns annotations
"""
import chess
from typing import Dict, List, Optional, Tuple


class MoveAnnotator:
    """Annotates chess moves based on quality"""
    
    # Annotation symbols
    BRILLIANT = "!!"  # Brilliant move
    GOOD = "!"  # Good move
    INTERESTING = "!?"  # Interesting move
    DUBIOUS = "?!"  # Dubious move
    MISTAKE = "?"  # Mistake
    BLUNDER = "??"  # Blunder
    
    def __init__(self):
        self.annotations = {}
        
    def annotate_move(self, 
                     move_san: str, 
                     move_number: int,
                     eval_before: Optional[float] = None,
                     eval_after: Optional[float] = None,
                     best_move: Optional[str] = None,
                     is_book_move: bool = False) -> str:
        """
        Annotate a move based on evaluation changes
        
        Args:
            move_san: Move in SAN notation
            move_number: Move number
            eval_before: Evaluation before the move (in pawns, positive = white advantage)
            eval_after: Evaluation after the move
            best_move: The best move according to engine
            is_book_move: Whether the move is from opening theory
            
        Returns:
            Annotated move string
        """
        if is_book_move:
            # Book moves don't get annotations
            self.annotations[move_number] = {
                'move': move_san,
                'annotation': 'book',
                'description': 'Coup théorique'
            }
            return move_san
            
        if eval_before is None or eval_after is None:
            # No evaluation available
            return move_san
            
        # Calculate evaluation loss (from player's perspective)
        # Note: eval is from white's perspective, so we need to flip for black
        move_is_white = (move_number % 2 == 1)
        
        if move_is_white:
            eval_loss = eval_before - eval_after
        else:
            eval_loss = eval_after - eval_before
            
        annotation = ""
        description = ""
        
        # Determine annotation based on eval loss
        if eval_loss < -1.5:
            # Position improved significantly
            annotation = self.BRILLIANT
            description = "Coup brillant!"
        elif eval_loss < -0.5:
            # Good improvement
            annotation = self.GOOD
            description = "Bon coup"
        elif -0.5 <= eval_loss <= 0.3:
            # Acceptable move
            if move_san == best_move:
                annotation = self.GOOD
                description = "Meilleur coup"
            else:
                annotation = ""
                description = "Coup acceptable"
        elif 0.3 < eval_loss <= 1.0:
            # Slight inaccuracy
            annotation = self.INTERESTING
            description = "Imprécision"
        elif 1.0 < eval_loss <= 2.5:
            # Mistake
            annotation = self.MISTAKE
            description = "Erreur"
        elif 2.5 < eval_loss <= 5.0:
            # Serious mistake
            annotation = self.MISTAKE
            description = "Erreur sérieuse"
        else:
            # Blunder
            annotation = self.BLUNDER
            description = "Gaffe!"
            
        self.annotations[move_number] = {
            'move': move_san,
            'annotation': annotation,
            'description': description,
            'eval_loss': eval_loss,
            'eval_before': eval_before,
            'eval_after': eval_after,
            'best_move': best_move
        }
        
        return f"{move_san}{annotation}" if annotation else move_san
        
    def get_annotation_for_move(self, move_number: int) -> Dict:
        """Get annotation details for a move"""
        return self.annotations.get(move_number, {})
        
    def get_all_annotations(self) -> Dict[int, Dict]:
        """Get all move annotations"""
        return self.annotations
        
    def get_statistics(self) -> Dict:
        """Get statistics on move quality"""
        stats = {
            'brilliant': 0,
            'good': 0,
            'interesting': 0,
            'mistake': 0,
            'blunder': 0,
            'book': 0,
            'total': len(self.annotations)
        }
        
        for ann in self.annotations.values():
            annotation = ann.get('annotation', '')
            if annotation == self.BRILLIANT:
                stats['brilliant'] += 1
            elif annotation == self.GOOD:
                stats['good'] += 1
            elif annotation in [self.INTERESTING, self.DUBIOUS]:
                stats['interesting'] += 1
            elif annotation == self.MISTAKE:
                stats['mistake'] += 1
            elif annotation == self.BLUNDER:
                stats['blunder'] += 1
            elif annotation == 'book':
                stats['book'] += 1
                
        return stats
        
    def get_accuracy(self, is_white: bool = True) -> float:
        """
        Calculate player accuracy (0-100%)
        
        Args:
            is_white: Calculate for white (True) or black (False)
        """
        player_moves = []
        
        for move_num, ann in self.annotations.items():
            move_is_white = (move_num % 2 == 1)
            if move_is_white == is_white:
                player_moves.append(ann)
                
        if not player_moves:
            return 100.0
            
        total_error = 0.0
        for ann in player_moves:
            eval_loss = ann.get('eval_loss', 0)
            # Only count losses (positive eval_loss)
            if eval_loss > 0:
                total_error += eval_loss
                
        # Accuracy formula: 100 - (average_error * 10)
        # Cap at 0% minimum
        avg_error = total_error / len(player_moves)
        accuracy = max(0, 100 - (avg_error * 10))
        
        return round(accuracy, 1)

