"""
Notation panel for displaying PGN moves
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class NotationPanel(QWidget):
    """Widget for displaying chess notation in PGN format"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("📋 Notation PGN")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Text area for moves
        self.moves_text = QTextEdit()
        self.moves_text.setReadOnly(True)
        self.moves_text.setPlaceholderText("Les coups apparaîtront ici...")
        
        # Custom styling for better readability
        self.moves_text.setStyleSheet("""
            QTextEdit {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12pt;
                line-height: 1.6;
            }
        """)
        
        layout.addWidget(self.moves_text)
        
        # Game info section
        self.info_label = QLabel("Nouvelle partie")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 8px;
                color: #d4d4d4;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.info_label)
        
    def update_moves(self, pgn_text: str):
        """
        Update the moves display
        
        Args:
            pgn_text: PGN formatted move text
        """
        self.moves_text.setPlainText(pgn_text)
        # Scroll to bottom to show latest move
        cursor = self.moves_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.moves_text.setTextCursor(cursor)
        
    def append_move(self, move_number: int, white_move: str, black_move: str = ""):
        """
        Append a move to the notation
        
        Args:
            move_number: The move number
            white_move: White's move in SAN notation
            black_move: Black's move in SAN notation (optional)
        """
        current_text = self.moves_text.toPlainText()
        
        if black_move:
            new_text = f"{move_number}. {white_move} {black_move}\n"
        else:
            new_text = f"{move_number}. {white_move} "
            
        self.moves_text.setPlainText(current_text + new_text)
        
        # Scroll to bottom
        cursor = self.moves_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.moves_text.setTextCursor(cursor)
        
    def clear(self):
        """Clear all moves"""
        self.moves_text.clear()
        
    def set_game_info(self, info: str):
        """
        Set game information display
        
        Args:
            info: Information text to display
        """
        self.info_label.setText(info)
        
    def get_pgn(self) -> str:
        """Get the current PGN text"""
        return self.moves_text.toPlainText()

