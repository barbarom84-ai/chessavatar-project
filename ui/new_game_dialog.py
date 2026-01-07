"""
New Game Dialog - Configure game settings before starting
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QRadioButton, QButtonGroup,
                             QComboBox, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import chess


class NewGameDialog(QDialog):
    """Dialog for configuring a new game"""
    
    def __init__(self, engine_available=False, avatar_available=False, avatars=None, engines=None, parent=None):
        super().__init__(parent)
        self.engine_available = engine_available
        self.avatar_available = avatar_available
        self.avatars = avatars or []  # List of Avatar objects
        self.engines = engines or []  # List of EngineInfo objects
        
        # Default values
        self.mode = "free"
        self.player_color = chess.WHITE
        self.time_control = None
        self.selected_avatar_id = None
        self.selected_engine_name = None  # Selected engine for vs_engine mode
        self.selected_white_engine_name = None  # For AI vs AI modes
        self.selected_black_engine_name = None  # For AI vs AI modes
        
        self.init_ui()
        self.apply_theme()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Nouvelle Partie")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Configuration de la Partie")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Mode selection
        mode_group = QGroupBox("Mode de jeu")
        mode_layout = QVBoxLayout()
        
        self.mode_group = QButtonGroup()
        
        self.free_radio = QRadioButton("Partie libre (analyse)")
        self.free_radio.setChecked(True)
        self.free_radio.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.free_radio, 0)
        mode_layout.addWidget(self.free_radio)
        
        self.vs_engine_radio = QRadioButton("Jouer contre le moteur")
        self.vs_engine_radio.setEnabled(self.engine_available)
        self.vs_engine_radio.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.vs_engine_radio, 1)
        mode_layout.addWidget(self.vs_engine_radio)
        
        if not self.engine_available:
            no_engine_label = QLabel("   Aucun moteur configure")
            no_engine_label.setStyleSheet("color: #ff6b6b; font-size: 9pt;")
            mode_layout.addWidget(no_engine_label)
        
        self.vs_avatar_radio = QRadioButton("Jouer contre un avatar")
        self.vs_avatar_radio.setEnabled(self.avatar_available)
        self.vs_avatar_radio.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.vs_avatar_radio, 2)
        mode_layout.addWidget(self.vs_avatar_radio)
        
        if not self.avatar_available:
            no_avatar_label = QLabel("   Aucun avatar configuré")
            no_avatar_label.setStyleSheet("color: #888888; font-size: 9pt;")
            mode_layout.addWidget(no_avatar_label)
        
        # NEW: Human vs Human mode
        self.vs_human_radio = QRadioButton("Humain vs Humain (local)")
        self.vs_human_radio.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.vs_human_radio, 3)
        mode_layout.addWidget(self.vs_human_radio)
        
        # NEW: AI vs AI modes
        mode_layout.addWidget(QLabel(""))  # Separator
        ai_label = QLabel("🤖 Modes IA vs IA (Observer)")
        ai_label.setStyleSheet("color: #4FC3F7; font-weight: bold; font-size: 10pt; margin-top: 5px;")
        mode_layout.addWidget(ai_label)
        
        self.engine_vs_engine_radio = QRadioButton("⚔️ Moteur vs Moteur")
        self.engine_vs_engine_radio.setEnabled(self.engine_available)
        self.engine_vs_engine_radio.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.engine_vs_engine_radio, 4)
        mode_layout.addWidget(self.engine_vs_engine_radio)
        
        if not self.engine_available:
            no_engine_ai_label = QLabel("   Aucun moteur configuré")
            no_engine_ai_label.setStyleSheet("color: #ff6b6b; font-size: 9pt;")
            mode_layout.addWidget(no_engine_ai_label)
        
        self.avatar_vs_avatar_radio = QRadioButton("👥 Avatar vs Avatar")
        self.avatar_vs_avatar_radio.setEnabled(len(self.avatars) >= 2)
        self.avatar_vs_avatar_radio.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.avatar_vs_avatar_radio, 5)
        mode_layout.addWidget(self.avatar_vs_avatar_radio)
        
        if len(self.avatars) < 2:
            no_2avatars_label = QLabel("   Au moins 2 avatars requis")
            no_2avatars_label.setStyleSheet("color: #888888; font-size: 9pt;")
            mode_layout.addWidget(no_2avatars_label)
        
        self.avatar_vs_engine_radio = QRadioButton("🤖 Avatar vs Moteur")
        self.avatar_vs_engine_radio.setEnabled(self.engine_available and self.avatar_available)
        self.avatar_vs_engine_radio.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.avatar_vs_engine_radio, 6)
        mode_layout.addWidget(self.avatar_vs_engine_radio)
        
        if not (self.engine_available and self.avatar_available):
            no_both_label = QLabel("   Moteur ET avatar requis")
            no_both_label.setStyleSheet("color: #888888; font-size: 9pt;")
            mode_layout.addWidget(no_both_label)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # Color selection (visible only for vs_engine/vs_avatar)
        self.color_group_widget = QGroupBox("Jouer avec")
        color_layout = QHBoxLayout()
        
        self.color_group = QButtonGroup()
        
        self.white_radio = QRadioButton("Blancs")
        self.white_radio.setChecked(True)
        self.color_group.addButton(self.white_radio, 0)
        color_layout.addWidget(self.white_radio)
        
        self.black_radio = QRadioButton("Noirs")
        self.color_group.addButton(self.black_radio, 1)
        color_layout.addWidget(self.black_radio)
        
        self.random_radio = QRadioButton("Aleatoire")
        self.color_group.addButton(self.random_radio, 2)
        color_layout.addWidget(self.random_radio)
        
        self.color_group_widget.setLayout(color_layout)
        self.color_group_widget.setVisible(False)  # Hidden by default
        layout.addWidget(self.color_group_widget)
        
        # Avatar selection (visible only for vs_avatar mode)
        self.avatar_group_widget = QGroupBox("Choisir un avatar")
        avatar_layout = QVBoxLayout()
        
        self.avatar_combo = QComboBox()
        self.avatar_combo.setMinimumHeight(35)
        if self.avatars:
            for avatar in self.avatars:
                # Display: "Name (Elo) - Platform"
                elo = avatar.style_data.get('average_elo', 'N/A')
                display_text = f"{avatar.display_name} ({elo}) - {avatar.platform.title()}"
                self.avatar_combo.addItem(display_text, avatar.id)
        else:
            self.avatar_combo.addItem("Aucun avatar disponible", None)
            self.avatar_combo.setEnabled(False)
        
        avatar_layout.addWidget(self.avatar_combo)
        
        # Avatar info label
        self.avatar_info_label = QLabel("")
        self.avatar_info_label.setStyleSheet("color: #888888; font-size: 9pt; padding: 5px;")
        self.avatar_info_label.setWordWrap(True)
        avatar_layout.addWidget(self.avatar_info_label)
        
        self.avatar_combo.currentIndexChanged.connect(self.on_avatar_changed)
        
        self.avatar_group_widget.setLayout(avatar_layout)
        self.avatar_group_widget.setVisible(False)  # Hidden by default
        layout.addWidget(self.avatar_group_widget)
        
        # Engine selection (visible for vs_engine mode)
        self.engine_group_widget = QGroupBox("Choisir un moteur")
        engine_layout = QVBoxLayout()
        
        self.engine_combo = QComboBox()
        self.engine_combo.setMinimumHeight(35)
        if self.engines:
            for engine in self.engines:
                protocol = engine.protocol if hasattr(engine, 'protocol') else 'UCI'
                display_text = f"{engine.name} ({protocol})"
                self.engine_combo.addItem(display_text, engine.name)
        else:
            self.engine_combo.addItem("Aucun moteur disponible", None)
            self.engine_combo.setEnabled(False)
        
        engine_layout.addWidget(self.engine_combo)
        
        # Engine info label
        self.engine_info_label = QLabel("")
        self.engine_info_label.setStyleSheet("color: #888888; font-size: 9pt; padding: 5px;")
        engine_layout.addWidget(self.engine_info_label)
        
        self.engine_combo.currentIndexChanged.connect(self.on_engine_changed)
        
        self.engine_group_widget.setLayout(engine_layout)
        self.engine_group_widget.setVisible(False)  # Hidden by default
        layout.addWidget(self.engine_group_widget)
        
        # Second avatar selection (for Avatar vs Avatar mode)
        self.avatar2_group_widget = QGroupBox("Choisir le second avatar")
        avatar2_layout = QVBoxLayout()
        
        self.avatar2_combo = QComboBox()
        self.avatar2_combo.setMinimumHeight(35)
        if self.avatars:
            for avatar in self.avatars:
                elo = avatar.style_data.get('average_elo', 'N/A')
                display_text = f"{avatar.display_name} ({elo}) - {avatar.platform.title()}"
                self.avatar2_combo.addItem(display_text, avatar.id)
        else:
            self.avatar2_combo.addItem("Aucun avatar disponible", None)
            self.avatar2_combo.setEnabled(False)
        
        avatar2_layout.addWidget(self.avatar2_combo)
        
        # Avatar 2 info label
        self.avatar2_info_label = QLabel("")
        self.avatar2_info_label.setStyleSheet("color: #888888; font-size: 9pt; padding: 5px;")
        self.avatar2_info_label.setWordWrap(True)
        avatar2_layout.addWidget(self.avatar2_info_label)
        
        self.avatar2_combo.currentIndexChanged.connect(self.on_avatar2_changed)
        
        self.avatar2_group_widget.setLayout(avatar2_layout)
        self.avatar2_group_widget.setVisible(False)  # Hidden by default
        layout.addWidget(self.avatar2_group_widget)
        
        # Update avatar2 info if avatars exist
        if len(self.avatars) >= 2:
            self.avatar2_combo.setCurrentIndex(1)  # Select second avatar by default
            self.on_avatar2_changed(1)
        
        # Update avatar info if avatars exist
        if self.avatars:
            self.on_avatar_changed(0)
        
        # Time control selection (optional)
        time_group = QGroupBox("Cadence (optionnel)")
        time_layout = QFormLayout()
        
        self.time_combo = QComboBox()
        self.time_combo.addItem("Conserver la cadence actuelle", None)
        self.time_combo.addItem("Bullet 1+0", "Bullet 1+0")
        self.time_combo.addItem("Bullet 2+1", "Bullet 2+1")
        self.time_combo.addItem("Blitz 3+0", "Blitz 3+0")
        self.time_combo.addItem("Blitz 3+2", "Blitz 3+2")
        self.time_combo.addItem("Blitz 5+0", "Blitz 5+0")
        self.time_combo.addItem("Rapid 10+0", "Rapid 10+0")
        self.time_combo.addItem("Rapid 15+10", "Rapid 15+10")
        self.time_combo.addItem("Classical 30+0", "Classical 30+0")
        time_layout.addRow("Cadence:", self.time_combo)
        
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setMinimumHeight(35)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("Commencer")
        ok_btn.setMinimumHeight(35)
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_mode_changed(self):
        """Handle mode change"""
        if self.vs_engine_radio.isChecked():
            self.color_group_widget.setVisible(True)
            self.avatar_group_widget.setVisible(False)
            self.engine_group_widget.setVisible(True if self.engines else False)
            self.avatar2_group_widget.setVisible(False)
        elif self.vs_avatar_radio.isChecked():
            self.color_group_widget.setVisible(True)
            self.avatar_group_widget.setVisible(True)
            self.engine_group_widget.setVisible(False)
            self.avatar2_group_widget.setVisible(False)
        elif self.vs_human_radio.isChecked():
            # Human vs Human: hide color and avatar selection
            self.color_group_widget.setVisible(False)
            self.avatar_group_widget.setVisible(False)
            self.engine_group_widget.setVisible(False)
            self.avatar2_group_widget.setVisible(False)
        elif self.engine_vs_engine_radio.isChecked():
            # Engine vs Engine: hide all player selections
            self.color_group_widget.setVisible(False)
            self.avatar_group_widget.setVisible(False)
            self.engine_group_widget.setVisible(False)
            self.avatar2_group_widget.setVisible(False)
        elif self.avatar_vs_avatar_radio.isChecked():
            # Avatar vs Avatar: show both avatar selections
            self.color_group_widget.setVisible(False)
            self.avatar_group_widget.setVisible(True)
            self.engine_group_widget.setVisible(False)
            self.avatar2_group_widget.setVisible(True)
        elif self.avatar_vs_engine_radio.isChecked():
            # Avatar vs Engine: show avatar selection only
            self.color_group_widget.setVisible(False)
            self.avatar_group_widget.setVisible(True)
            self.engine_group_widget.setVisible(False)
            self.avatar2_group_widget.setVisible(False)
        else:
            self.color_group_widget.setVisible(False)
            self.avatar_group_widget.setVisible(False)
            self.engine_group_widget.setVisible(False)
            self.avatar2_group_widget.setVisible(False)
    
    def on_engine_changed(self, index):
        """Handle engine selection change"""
        if index >= 0 and index < len(self.engines):
            engine = self.engines[index]
            self.selected_engine_name = engine.name
            protocol = engine.protocol if hasattr(engine, 'protocol') else 'UCI'
            self.engine_info_label.setText(f"Protocole: {protocol}")
        else:
            self.selected_engine_name = None
            self.engine_info_label.setText("")
    
    def on_avatar_changed(self, index):
        """Handle avatar selection change"""
        if index < 0 or index >= len(self.avatars):
            self.avatar_info_label.setText("")
            return
        
        avatar = self.avatars[index]
        
        # Display avatar info
        elo = avatar.style_data.get('average_elo', 'N/A')
        win_rate = avatar.style_data.get('win_rate', 0) * 100
        style = avatar.style_data.get('play_style', 'Équilibré')
        
        info_text = f"Elo: {elo} | Victoires: {win_rate:.0f}% | Style: {style}"
        self.avatar_info_label.setText(info_text)
    
    def on_avatar2_changed(self, index):
        """Handle second avatar selection change"""
        if index < 0 or index >= len(self.avatars):
            self.avatar2_info_label.setText("")
            return
        
        avatar = self.avatars[index]
        
        # Display avatar info
        elo = avatar.style_data.get('average_elo', 'N/A')
        win_rate = avatar.style_data.get('win_rate', 0) * 100
        style = avatar.style_data.get('play_style', 'Équilibré')
        
        info_text = f"Elo: {elo} | Victoires: {win_rate:.0f}% | Style: {style}"
        self.avatar2_info_label.setText(info_text)
    
    def get_config(self):
        """Return the game configuration"""
        import random
        
        # Determine mode
        if self.vs_engine_radio.isChecked():
            mode = "vs_engine"
        elif self.vs_avatar_radio.isChecked():
            mode = "vs_avatar"
        elif self.vs_human_radio.isChecked():
            mode = "vs_human"  # Human vs Human mode
        elif self.engine_vs_engine_radio.isChecked():
            mode = "engine_vs_engine"  # NEW: Engine vs Engine
        elif self.avatar_vs_avatar_radio.isChecked():
            mode = "avatar_vs_avatar"  # NEW: Avatar vs Avatar
        elif self.avatar_vs_engine_radio.isChecked():
            mode = "avatar_vs_engine"  # NEW: Avatar vs Engine
        else:
            mode = "free"
        
        # Determine color
        if self.random_radio.isChecked():
            player_color = random.choice([chess.WHITE, chess.BLACK])
        elif self.black_radio.isChecked():
            player_color = chess.BLACK
        else:
            player_color = chess.WHITE
        
        # Get time control
        time_control = self.time_combo.currentData()
        
        # Get selected avatar ID
        avatar_id = None
        if mode in ["vs_avatar", "avatar_vs_avatar", "avatar_vs_engine"] and self.avatar_combo.currentData():
            avatar_id = self.avatar_combo.currentData()
        
        # Get second avatar ID (for Avatar vs Avatar)
        avatar2_id = None
        if mode == "avatar_vs_avatar" and self.avatar2_combo.currentData():
            avatar2_id = self.avatar2_combo.currentData()
        
        # Get selected engine name
        engine_name = None
        if mode == "vs_engine" and self.selected_engine_name:
            engine_name = self.selected_engine_name
        
        return {
            'mode': mode,
            'player_color': player_color,
            'time_control': time_control,
            'avatar_id': avatar_id,
            'avatar2_id': avatar2_id,  # NEW: Second avatar
            'engine_name': engine_name  # NEW: Selected engine
        }
    
    def apply_theme(self):
        """Apply dark theme"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                margin-top: 12px;
                font-weight: bold;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QRadioButton {
                color: #d4d4d4;
                spacing: 8px;
            }
            QComboBox {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5689;
            }
        """)

