"""
Game Over Dialog - Shows the result of a chess game
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class GameOverDialog(QDialog):
    """Dialog to show game over result"""
    
    new_game_requested = pyqtSignal()
    
    def __init__(self, result: str, reason: str, parent=None):
        super().__init__(parent)
        self.result = result  # "1-0", "0-1", "1/2-1/2"
        self.reason = reason  # "Échec et mat", "Pat", etc.
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Partie Terminée")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # Debug logs
        print(f"DEBUG: GameOverDialog - result='{self.result}', reason='{self.reason}'")
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Icon and title based on result
        icon_label = QLabel()
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel()
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Determine icon and title - check reason for context
        reason_lower = self.reason.lower()
        is_draw = ("nulle" in reason_lower or 
                   "pat" in reason_lower or
                   "matériel insuffisant" in reason_lower or
                   "répétition" in reason_lower or
                   "50 coups" in reason_lower)
        
        # Priority 1: Use result if it's valid PGN notation
        if self.result == "1-0":
            icon_label.setText("🏆")
            title_label.setText("Victoire des Blancs !")
            title_label.setStyleSheet("color: #4CAF50;")
        elif self.result == "0-1":
            icon_label.setText("🏆")
            title_label.setText("Victoire des Noirs !")
            title_label.setStyleSheet("color: #4CAF50;")
        elif self.result == "1/2-1/2" or is_draw:
            icon_label.setText("🤝")
            title_label.setText("Match Nul")
            title_label.setStyleSheet("color: #FFC107;")
        # Priority 2: Fallback to reason if result is missing/invalid
        else:
            # Try to determine winner from reason
            if ("mat" in reason_lower or "abandon" in reason_lower):
                if "blancs" in reason_lower:
                    # Blancs ont perdu → Noirs gagnent
                    icon_label.setText("🏆")
                    title_label.setText("Victoire des Noirs !")
                    title_label.setStyleSheet("color: #4CAF50;")
                elif "noirs" in reason_lower:
                    # Noirs ont perdu → Blancs gagnent
                    icon_label.setText("🏆")
                    title_label.setText("Victoire des Blancs !")
                    title_label.setStyleSheet("color: #4CAF50;")
                else:
                    # Indéterminé
                    icon_label.setText("🏆")
                    title_label.setText("Partie Terminée")
                    title_label.setStyleSheet("color: #4CAF50;")
            elif is_draw:
                icon_label.setText("🤝")
                title_label.setText("Match Nul")
                title_label.setStyleSheet("color: #FFC107;")
            else:
                # Fallback total
                icon_label.setText("🏆")
                title_label.setText("Partie Terminée")
                title_label.setStyleSheet("color: #4CAF50;")
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        
        # Reason label
        reason_label = QLabel(self.reason)
        reason_font = QFont()
        reason_font.setPointSize(12)
        reason_label.setFont(reason_font)
        reason_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        reason_label.setStyleSheet("color: #aaaaaa;")
        layout.addWidget(reason_label)
        
        # Result label (PGN notation)
        result_label = QLabel(f"Résultat : {self.result}")
        result_font = QFont()
        result_font.setPointSize(11)
        result_label.setFont(result_font)
        result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_label.setStyleSheet("color: #888888;")
        layout.addWidget(result_label)
        
        # Spacer
        layout.addSpacing(10)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # New game button
        new_game_btn = QPushButton("Nouvelle Partie")
        new_game_btn.setMinimumHeight(40)
        new_game_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_game_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        new_game_btn.clicked.connect(self.on_new_game)
        button_layout.addWidget(new_game_btn)
        
        # Close button
        close_btn = QPushButton("Fermer")
        close_btn.setMinimumHeight(40)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """)
    
    def on_new_game(self):
        """Handle new game button click"""
        self.new_game_requested.emit()
        self.accept()

