"""
Notation panel for displaying PGN moves with navigation
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLabel, QPushButton, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class NotationPanel(QWidget):
    """Widget for displaying chess notation in PGN format with navigation"""
    
    # Signal émis quand on navigue vers un coup
    move_selected = pyqtSignal(int)  # Index du coup (0 = position de départ)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.moves_list = []  # Liste des coups en notation SAN
        self.current_move_index = 0  # Index du coup courant
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
        
        # Liste des coups (cliquable)
        self.moves_list_widget = QListWidget()
        self.moves_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11pt;
            }
            QListWidget::item {
                padding: 4px;
                border-radius: 2px;
            }
            QListWidget::item:selected {
                background-color: #094771;
            }
            QListWidget::item:hover {
                background-color: #2a2d2e;
            }
        """)
        self.moves_list_widget.itemClicked.connect(self.on_move_clicked)
        layout.addWidget(self.moves_list_widget)
        
        # Boutons de navigation
        nav_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("⏮ Début")
        self.btn_start.clicked.connect(self.go_to_start)
        self.btn_start.setToolTip("Aller au début de la partie")
        nav_layout.addWidget(self.btn_start)
        
        self.btn_prev = QPushButton("◀ Préc")
        self.btn_prev.clicked.connect(self.go_to_previous)
        self.btn_prev.setToolTip("Coup précédent (←)")
        nav_layout.addWidget(self.btn_prev)
        
        self.btn_next = QPushButton("Suiv ▶")
        self.btn_next.clicked.connect(self.go_to_next)
        self.btn_next.setToolTip("Coup suivant (→)")
        nav_layout.addWidget(self.btn_next)
        
        self.btn_end = QPushButton("Fin ⏭")
        self.btn_end.clicked.connect(self.go_to_end)
        self.btn_end.setToolTip("Aller à la fin de la partie")
        nav_layout.addWidget(self.btn_end)
        
        # Style des boutons
        button_style = """
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5689;
            }
            QPushButton:disabled {
                background-color: #3e3e3e;
                color: #888888;
            }
        """
        self.btn_start.setStyleSheet(button_style)
        self.btn_prev.setStyleSheet(button_style)
        self.btn_next.setStyleSheet(button_style)
        self.btn_end.setStyleSheet(button_style)
        
        layout.addLayout(nav_layout)
        
        # Position indicator
        self.position_label = QLabel("Position: 0/0")
        self.position_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.position_label.setStyleSheet("color: #888888; font-size: 9pt;")
        layout.addWidget(self.position_label)
        
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
        
        self.update_buttons_state()
        
    def update_moves(self, pgn_text: str):
        """
        Update the moves display
        
        Args:
            pgn_text: PGN formatted move text (e.g., "1. e4 e5 2. Nf3 Nc6")
        """
        # Parser le texte PGN pour extraire les coups
        self.moves_list = []
        
        if pgn_text.strip():
            # Retirer les numéros de coups et splitter
            import re
            # Enlever les numéros de coups (1. 2. etc.)
            moves_only = re.sub(r'\d+\.', '', pgn_text)
            # Splitter et nettoyer
            moves = [m.strip() for m in moves_only.split() if m.strip()]
            self.moves_list = moves
        
        # Mettre à jour la liste widget
        self.moves_list_widget.clear()
        
        # Ajouter position de départ
        item = QListWidgetItem("⭐ Position de départ")
        self.moves_list_widget.addItem(item)
        
        # Ajouter les coups
        for i, move in enumerate(self.moves_list):
            move_num = (i // 2) + 1
            color = "Blancs" if i % 2 == 0 else "Noirs"
            item_text = f"{move_num}. {move} ({color})"
            item = QListWidgetItem(item_text)
            self.moves_list_widget.addItem(item)
        
        # Aller à la fin par défaut
        self.current_move_index = len(self.moves_list)
        self.update_position_display()
        self.update_buttons_state()
        
        # Sélectionner le dernier coup
        if self.current_move_index > 0:
            self.moves_list_widget.setCurrentRow(self.current_move_index)
        
    def on_move_clicked(self, item):
        """Handle click on a move in the list"""
        index = self.moves_list_widget.row(item)
        self.current_move_index = index
        self.move_selected.emit(index)
        self.update_position_display()
        self.update_buttons_state()
        
    def go_to_start(self):
        """Go to the start position"""
        self.current_move_index = 0
        self.moves_list_widget.setCurrentRow(0)
        self.move_selected.emit(0)
        self.update_position_display()
        self.update_buttons_state()
        
    def go_to_previous(self):
        """Go to previous move"""
        if self.current_move_index > 0:
            self.current_move_index -= 1
            self.moves_list_widget.setCurrentRow(self.current_move_index)
            self.move_selected.emit(self.current_move_index)
            self.update_position_display()
            self.update_buttons_state()
            
    def go_to_next(self):
        """Go to next move"""
        if self.current_move_index < len(self.moves_list):
            self.current_move_index += 1
            self.moves_list_widget.setCurrentRow(self.current_move_index)
            self.move_selected.emit(self.current_move_index)
            self.update_position_display()
            self.update_buttons_state()
            
    def go_to_end(self):
        """Go to the end position"""
        self.current_move_index = len(self.moves_list)
        self.moves_list_widget.setCurrentRow(self.current_move_index)
        self.move_selected.emit(self.current_move_index)
        self.update_position_display()
        self.update_buttons_state()
        
    def update_position_display(self):
        """Update the position indicator"""
        total = len(self.moves_list)
        self.position_label.setText(f"Position: {self.current_move_index}/{total}")
        
    def update_buttons_state(self):
        """Update enabled/disabled state of navigation buttons"""
        self.btn_start.setEnabled(self.current_move_index > 0)
        self.btn_prev.setEnabled(self.current_move_index > 0)
        self.btn_next.setEnabled(self.current_move_index < len(self.moves_list))
        self.btn_end.setEnabled(self.current_move_index < len(self.moves_list))
        
    def append_move(self, move_number: int, white_move: str, black_move: str = ""):
        """
        Append a move to the notation
        
        Args:
            move_number: The move number
            white_move: White's move in SAN notation
            black_move: Black's move in SAN notation (optional)
        """
        if black_move:
            self.moves_list.append(white_move)
            self.moves_list.append(black_move)
        else:
            self.moves_list.append(white_move)
        
        # Reconstruire le texte PGN et mettre à jour
        pgn_text = self._build_pgn_text()
        self.update_moves(pgn_text)
        
    def _build_pgn_text(self) -> str:
        """Build PGN text from moves list"""
        pgn = []
        for i, move in enumerate(self.moves_list):
            if i % 2 == 0:
                pgn.append(f"{i//2 + 1}. {move}")
            else:
                pgn.append(move)
        return " ".join(pgn)
        
    def clear(self):
        """Clear all moves"""
        self.moves_list = []
        self.current_move_index = 0
        self.moves_list_widget.clear()
        
        # Ajouter position de départ
        item = QListWidgetItem("⭐ Position de départ")
        self.moves_list_widget.addItem(item)
        
        self.update_position_display()
        self.update_buttons_state()
        
    def set_game_info(self, info: str):
        """
        Set game information display
        
        Args:
            info: Information text to display
        """
        self.info_label.setText(info)
        
    def get_pgn(self) -> str:
        """Get the current PGN text"""
        return self._build_pgn_text()
    
    def keyPressEvent(self, event):
        """Handle keyboard navigation"""
        if event.key() == Qt.Key.Key_Left:
            self.go_to_previous()
        elif event.key() == Qt.Key.Key_Right:
            self.go_to_next()
        elif event.key() == Qt.Key.Key_Home:
            self.go_to_start()
        elif event.key() == Qt.Key.Key_End:
            self.go_to_end()
        else:
            super().keyPressEvent(event)
