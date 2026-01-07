"""
Theme and Piece Selection Dialog
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QComboBox, QLabel, QPushButton, QRadioButton,
                             QButtonGroup, QScrollArea, QWidget, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer

from core.board_themes import BoardThemes


class ThemeConfigDialog(QDialog):
    """Dialog for configuring board themes and piece sets"""
    
    # Signal émis quand la config change
    theme_changed = pyqtSignal(str, str)  # (theme_name, piece_set)
    
    def __init__(self, parent=None, current_theme="classic", current_piece_set="default"):
        super().__init__(parent)
        self.current_theme = current_theme
        self.current_piece_set = current_piece_set
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("🎨 Configuration des Thèmes et Pièces")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🎨 Personnalisation de l'Échiquier")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Choisissez votre thème de plateau et votre style de pièces préféré")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #888888; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Theme Selection
        theme_group = QGroupBox("🎨 Thème du Plateau")
        theme_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                padding-top: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        theme_layout = QVBoxLayout()
        
        # Scroll area for themes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(300)
        
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        
        # Get all themes
        self.theme_buttons = []
        self.theme_group = QButtonGroup()
        
        themes = [
            ("classic", "🏛️ Classique", "Vert et crème traditionnel"),
            ("wood", "🪵 Bois", "Marron chaud"),
            ("blue", "🌊 Océan", "Bleu profond"),
            ("green", "🌲 Forêt", "Vert foncé"),
            ("brown", "🟤 Terre", "Marron clair"),
            ("gray", "⚪ Minimaliste", "Gris moderne"),
            ("neon", "💡 Néon", "Cyan et magenta"),
            ("candy", "🍬 Bonbon", "Rose et violet"),
            ("tournament", "🏆 Tournoi", "Vert officiel"),
            ("newspaper", "📰 Journal", "Noir et blanc"),
            ("coral", "🪸 Corail", "Orange doux"),
            ("purple", "🟣 Améthyste", "Violet"),
            ("marble", "🗿 Marbre", "Gris pierre"),
            ("metal", "⚙️ Métal", "Argenté"),
            ("sandstone", "🏜️ Grès", "Beige sable"),
            ("colorblind", "👁️ Daltonisme", "Optimisé accessibilité")
        ]
        
        row = 0
        col = 0
        for theme_id, theme_name, theme_desc in themes:
            # Créer un widget pour chaque thème
            theme_widget = QWidget()
            theme_widget_layout = QVBoxLayout(theme_widget)
            theme_widget_layout.setContentsMargins(5, 5, 5, 5)
            
            # Radio button
            radio = QRadioButton(theme_name)
            radio.setProperty("theme_id", theme_id)
            if theme_id == self.current_theme:
                radio.setChecked(True)
            self.theme_group.addButton(radio)
            self.theme_buttons.append(radio)
            
            # Description
            desc_label = QLabel(theme_desc)
            desc_label.setStyleSheet("color: #888888; font-size: 9pt;")
            desc_label.setWordWrap(True)
            
            # Preview miniature
            preview = self.create_theme_preview(theme_id)
            
            theme_widget_layout.addWidget(radio)
            theme_widget_layout.addWidget(preview)
            theme_widget_layout.addWidget(desc_label)
            
            theme_widget.setStyleSheet("""
                QWidget {
                    background-color: #2d2d30;
                    border: 2px solid #3e3e3e;
                    border-radius: 6px;
                    padding: 8px;
                }
                QWidget:hover {
                    border-color: #0e639c;
                }
            """)
            
            scroll_layout.addWidget(theme_widget, row, col)
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        scroll.setWidget(scroll_widget)
        theme_layout.addWidget(scroll)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Piece Set Selection
        pieces_group = QGroupBox("♟️ Style des Pièces")
        pieces_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                padding-top: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        pieces_layout = QVBoxLayout()
        
        piece_sets_layout = QHBoxLayout()
        
        self.piece_combo = QComboBox()
        self.piece_combo.addItem("⭐ ChessAvatar SVG (Défaut)", "svg")
        self.piece_combo.addItem("🎨 Unicode Bitmap", "default")
        self.piece_combo.addItem("🎭 Futur: Alpha", "alpha")
        self.piece_combo.addItem("🎭 Futur: Merida", "merida")
        self.piece_combo.addItem("🎭 Futur: Celtic", "celtic")
        
        # Désactiver les sets non implémentés
        for i in range(2, 5):
            self.piece_combo.model().item(i).setEnabled(False)
        
        # Sélectionner le set actuel
        index = self.piece_combo.findData(self.current_piece_set)
        if index >= 0:
            self.piece_combo.setCurrentIndex(index)
        
        self.piece_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 11pt;
                background-color: #2d2d30;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
            }
            QComboBox:hover {
                border-color: #0e639c;
            }
        """)
        
        piece_sets_layout.addWidget(QLabel("Style:"))
        piece_sets_layout.addWidget(self.piece_combo, stretch=1)
        
        pieces_layout.addLayout(piece_sets_layout)
        
        # Note sur ChessAvatar SVG
        svg_note = QLabel("⭐ ChessAvatar utilise des pièces SVG professionnelles de haute qualité")
        svg_note.setStyleSheet("color: #4ec9b0; font-size: 9pt; font-style: italic; padding: 5px;")
        svg_note.setWordWrap(True)
        pieces_layout.addWidget(svg_note)
        
        pieces_group.setLayout(pieces_layout)
        layout.addWidget(pieces_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("👁️ Aperçu")
        self.preview_btn.clicked.connect(self.on_preview)
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        
        self.apply_btn = QPushButton("✅ Appliquer")
        self.apply_btn.clicked.connect(self.on_apply)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e7d06;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0f9607;
            }
        """)
        
        self.cancel_btn = QPushButton("❌ Annuler")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3e3e3e;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        
        buttons_layout.addWidget(self.preview_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.apply_btn)
        
        layout.addLayout(buttons_layout)
        
    def create_theme_preview(self, theme_name: str):
        """Create a small preview of the theme"""
        preview_label = QLabel()
        preview_label.setFixedSize(120, 120)
        
        # Create pixmap
        pixmap = QPixmap(120, 120)
        painter = QPainter(pixmap)
        
        # Get theme colors
        theme_colors = BoardThemes.get_theme(theme_name)
        light_color = QColor(theme_colors["light"])
        dark_color = QColor(theme_colors["dark"])
        
        # Draw checkerboard pattern
        square_size = 30
        for row in range(4):
            for col in range(4):
                color = light_color if (row + col) % 2 == 0 else dark_color
                painter.fillRect(col * square_size, row * square_size, 
                               square_size, square_size, color)
        
        painter.end()
        preview_label.setPixmap(pixmap)
        
        return preview_label
        
    def on_preview(self):
        """Preview the selected theme"""
        selected_theme = None
        for button in self.theme_buttons:
            if button.isChecked():
                selected_theme = button.property("theme_id")
                break
        
        selected_piece_set = self.piece_combo.currentData()
        
        if selected_theme:
            # Émettre le signal pour preview
            self.theme_changed.emit(selected_theme, selected_piece_set)
            self.statusBar().showMessage(f"Aperçu: {selected_theme} + {selected_piece_set}", 2000)
        
    def on_apply(self):
        """Apply the selected theme and piece set"""
        selected_theme = None
        for button in self.theme_buttons:
            if button.isChecked():
                selected_theme = button.property("theme_id")
                break
        
        selected_piece_set = self.piece_combo.currentData()
        
        if selected_theme:
            self.current_theme = selected_theme
            self.current_piece_set = selected_piece_set
            self.theme_changed.emit(selected_theme, selected_piece_set)
            self.accept()
            
    def get_selected_theme(self):
        """Get the selected theme"""
        return self.current_theme
        
    def get_selected_piece_set(self):
        """Get the selected piece set"""
        return self.current_piece_set

