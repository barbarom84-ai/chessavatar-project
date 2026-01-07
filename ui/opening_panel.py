"""
Opening Panel - Display current opening information during game
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame,
                             QPushButton, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from core.opening_book import OpeningBook, Opening
import chess
from typing import Optional


class OpeningPanel(QWidget):
    """Panel to display opening information"""
    
    search_requested = pyqtSignal(str)  # Emits opening name for search
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.opening_book = OpeningBook()
        self.current_opening: Optional[Opening] = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("📚 Ouverture")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #d4d4d4;")
        layout.addWidget(title)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #3e3e3e;")
        layout.addWidget(separator)
        
        # Opening name
        self.opening_name = QLabel("Position de départ")
        self.opening_name.setWordWrap(True)
        self.opening_name.setStyleSheet("""
            color: #4FC3F7;
            font-size: 13pt;
            font-weight: bold;
            padding: 8px;
            background-color: #2a2a2a;
            border-radius: 4px;
        """)
        self.opening_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.opening_name)
        
        # ECO code
        self.eco_code = QLabel("—")
        self.eco_code.setStyleSheet("""
            color: #81C784;
            font-size: 11pt;
            font-weight: bold;
            padding: 4px;
        """)
        self.eco_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.eco_code)
        
        # Variation
        self.variation_label = QLabel("")
        self.variation_label.setWordWrap(True)
        self.variation_label.setStyleSheet("""
            color: #AAAAAA;
            font-size: 10pt;
            padding: 4px;
        """)
        self.variation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.variation_label.setVisible(False)
        layout.addWidget(self.variation_label)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setStyleSheet("background-color: #3e3e3e;")
        layout.addWidget(separator2)
        
        # Opening moves
        moves_label = QLabel("Coups théoriques:")
        moves_label.setStyleSheet("color: #AAAAAA; font-size: 9pt;")
        layout.addWidget(moves_label)
        
        self.moves_display = QLabel("")
        self.moves_display.setWordWrap(True)
        self.moves_display.setStyleSheet("""
            color: #d4d4d4;
            font-size: 10pt;
            padding: 8px;
            background-color: #1e1e1e;
            border: 1px solid #3e3e3e;
            border-radius: 4px;
        """)
        layout.addWidget(self.moves_display)
        
        # Statistics (placeholder for future)
        self.stats_label = QLabel("")
        self.stats_label.setWordWrap(True)
        self.stats_label.setStyleSheet("""
            color: #888888;
            font-size: 9pt;
            padding: 4px;
        """)
        self.stats_label.setVisible(False)
        layout.addWidget(self.stats_label)
        
        # Search button
        self.search_button = QPushButton("🔍 Rechercher cette ouverture")
        self.search_button.clicked.connect(self.on_search_clicked)
        self.search_button.setVisible(False)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: #d4d4d4;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #4e4e4e;
            }
            QPushButton:pressed {
                background-color: #383838;
            }
        """)
        layout.addWidget(self.search_button)
        
        # Add stretch
        layout.addStretch()
        
    def update_opening(self, board: chess.Board):
        """
        Update opening information based on current board position
        
        Args:
            board: Current chess board
        """
        # Recognize opening
        opening = self.opening_book.recognize_opening(board)
        
        if opening:
            self.current_opening = opening
            self.opening_name.setText(opening.name)
            self.eco_code.setText(f"ECO: {opening.eco}")
            
            if opening.variation:
                self.variation_label.setText(f"Variante: {opening.variation}")
                self.variation_label.setVisible(True)
            else:
                self.variation_label.setVisible(False)
                
            # Display moves
            if opening.move_list:
                moves_text = self._format_moves(opening.move_list)
                self.moves_display.setText(moves_text)
            else:
                self.moves_display.setText("—")
                
            self.search_button.setVisible(True)
        else:
            # No opening recognized
            if len(board.move_stack) == 0:
                self.opening_name.setText("Position de départ")
                self.eco_code.setText("—")
            else:
                self.opening_name.setText("Position non répertoriée")
                self.eco_code.setText("—")
                
            self.variation_label.setVisible(False)
            self.moves_display.setText("—")
            self.search_button.setVisible(False)
            self.current_opening = None
            
    def _format_moves(self, move_list: list) -> str:
        """
        Format move list for display
        
        Args:
            move_list: List of UCI moves
            
        Returns:
            Formatted move string
        """
        # Convert UCI moves to SAN notation
        board = chess.Board()
        moves_san = []
        
        for i, move_uci in enumerate(move_list):
            try:
                move = chess.Move.from_uci(move_uci)
                san = board.san(move)
                
                if i % 2 == 0:
                    moves_san.append(f"{i//2 + 1}. {san}")
                else:
                    moves_san.append(san)
                    
                board.push(move)
            except:
                break
                
        return " ".join(moves_san)
        
    def on_search_clicked(self):
        """Handle search button click"""
        if self.current_opening:
            self.search_requested.emit(self.current_opening.name)
            
    def reset(self):
        """Reset opening display"""
        self.opening_name.setText("Position de départ")
        self.eco_code.setText("—")
        self.variation_label.setVisible(False)
        self.moves_display.setText("—")
        self.search_button.setVisible(False)
        self.current_opening = None
        
    def get_eco_stats(self) -> dict:
        """
        Get statistics about ECO codes
        
        Returns:
            Dictionary with ECO statistics
        """
        eco_codes = self.opening_book.get_all_eco_codes()
        
        stats = {
            'total_openings': len(self.opening_book.openings),
            'eco_codes': len(eco_codes),
            'eco_ranges': {
                'A': len([e for e in eco_codes if e.startswith('A')]),
                'B': len([e for e in eco_codes if e.startswith('B')]),
                'C': len([e for e in eco_codes if e.startswith('C')]),
                'D': len([e for e in eco_codes if e.startswith('D')]),
                'E': len([e for e in eco_codes if e.startswith('E')])
            }
        }
        
        return stats

