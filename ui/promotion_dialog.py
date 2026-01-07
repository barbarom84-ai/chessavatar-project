"""
Pawn promotion dialog
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel)
from PyQt6.QtCore import Qt
import chess


class PromotionDialog(QDialog):
    """Dialog for choosing pawn promotion piece"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_piece = chess.QUEEN  # Default
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("Promotion du Pion")
        self.setModal(True)
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        # Label
        label = QLabel("Choisissez la pièce de promotion :")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # Buttons for each piece
        buttons_layout = QHBoxLayout()
        
        # Queen
        queen_btn = QPushButton("♕ Dame")
        queen_btn.clicked.connect(lambda: self.select_piece(chess.QUEEN))
        buttons_layout.addWidget(queen_btn)
        
        # Rook
        rook_btn = QPushButton("♖ Tour")
        rook_btn.clicked.connect(lambda: self.select_piece(chess.ROOK))
        buttons_layout.addWidget(rook_btn)
        
        layout.addLayout(buttons_layout)
        
        # Second row
        buttons_layout2 = QHBoxLayout()
        
        # Bishop
        bishop_btn = QPushButton("♗ Fou")
        bishop_btn.clicked.connect(lambda: self.select_piece(chess.BISHOP))
        buttons_layout2.addWidget(bishop_btn)
        
        # Knight
        knight_btn = QPushButton("♘ Cavalier")
        knight_btn.clicked.connect(lambda: self.select_piece(chess.KNIGHT))
        buttons_layout2.addWidget(knight_btn)
        
        layout.addLayout(buttons_layout2)
        
        self.setLayout(layout)
        
        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #e0e0e0;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 10px;
                font-size: 16px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #0d7377;
            }
            QPushButton:pressed {
                background-color: #0d7377;
            }
        """)
        
    def select_piece(self, piece_type: int):
        """Select a piece and close dialog"""
        self.selected_piece = piece_type
        self.accept()
        
    def get_selected_piece(self) -> int:
        """Get the selected piece type"""
        return self.selected_piece

