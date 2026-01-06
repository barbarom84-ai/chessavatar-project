"""
Board configuration dialog for customizing appearance
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QGroupBox, QFormLayout,
                             QColorDialog, QSlider, QCheckBox, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from typing import Dict
import json
from pathlib import Path


class BoardConfig:
    """Board configuration data class"""
    
    DEFAULT_CONFIG = {
        'light_square_color': '#f0d9b5',
        'dark_square_color': '#b58863',
        'highlight_color': '#646f40',
        'selected_color': '#829769',
        'legal_move_color': '#546e7a',
        'piece_style': 'unicode',  # unicode, merida, alpha
        'square_size': 70,
        'show_coordinates': True,
        'show_legal_moves': True,
        'sounds_enabled': True,
        'sound_volume': 0.7
    }
    
    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_file = Path("board_config.json")
        self.load()
        
    def load(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                print(f"Error loading board config: {e}")
                
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving board config: {e}")
            
    def get(self, key: str):
        """Get configuration value"""
        return self.config.get(key, self.DEFAULT_CONFIG.get(key))
        
    def set(self, key: str, value):
        """Set configuration value"""
        self.config[key] = value
        
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()


class BoardConfigDialog(QDialog):
    """Dialog for configuring board appearance"""
    
    config_changed = pyqtSignal(dict)  # Emits new configuration
    
    def __init__(self, board_config: BoardConfig, parent=None):
        super().__init__(parent)
        self.board_config = board_config
        self.temp_config = board_config.config.copy()
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Configuration de l'Échiquier")
        self.setMinimumSize(600, 700)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("⚙️ Configuration de l'Échiquier")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #d4d4d4;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Colors group
        colors_group = QGroupBox("Couleurs de l'Échiquier")
        colors_layout = QFormLayout(colors_group)
        
        # Light square color
        light_square_layout = QHBoxLayout()
        self.light_square_preview = QLabel("   ")
        self.light_square_preview.setStyleSheet(
            f"background-color: {self.temp_config['light_square_color']}; "
            "border: 1px solid #3e3e3e; border-radius: 4px;"
        )
        self.light_square_preview.setFixedSize(40, 40)
        light_square_layout.addWidget(self.light_square_preview)
        
        light_square_button = QPushButton("Choisir...")
        light_square_button.clicked.connect(lambda: self.choose_color('light_square_color', self.light_square_preview))
        light_square_layout.addWidget(light_square_button)
        light_square_layout.addStretch()
        colors_layout.addRow("Cases claires:", light_square_layout)
        
        # Dark square color
        dark_square_layout = QHBoxLayout()
        self.dark_square_preview = QLabel("   ")
        self.dark_square_preview.setStyleSheet(
            f"background-color: {self.temp_config['dark_square_color']}; "
            "border: 1px solid #3e3e3e; border-radius: 4px;"
        )
        self.dark_square_preview.setFixedSize(40, 40)
        dark_square_layout.addWidget(self.dark_square_preview)
        
        dark_square_button = QPushButton("Choisir...")
        dark_square_button.clicked.connect(lambda: self.choose_color('dark_square_color', self.dark_square_preview))
        dark_square_layout.addWidget(dark_square_button)
        dark_square_layout.addStretch()
        colors_layout.addRow("Cases foncées:", dark_square_layout)
        
        # Highlight color
        highlight_layout = QHBoxLayout()
        self.highlight_preview = QLabel("   ")
        self.highlight_preview.setStyleSheet(
            f"background-color: {self.temp_config['highlight_color']}; "
            "border: 1px solid #3e3e3e; border-radius: 4px;"
        )
        self.highlight_preview.setFixedSize(40, 40)
        highlight_layout.addWidget(self.highlight_preview)
        
        highlight_button = QPushButton("Choisir...")
        highlight_button.clicked.connect(lambda: self.choose_color('highlight_color', self.highlight_preview))
        highlight_layout.addWidget(highlight_button)
        highlight_layout.addStretch()
        colors_layout.addRow("Surbrillance:", highlight_layout)
        
        layout.addWidget(colors_group)
        
        # Piece style group
        pieces_group = QGroupBox("Style des Pièces")
        pieces_layout = QFormLayout(pieces_group)
        
        self.piece_style_combo = QComboBox()
        self.piece_style_combo.addItems(["Unicode ♔♕♖", "ASCII [K][Q][R]"])
        current_style = self.temp_config['piece_style']
        if current_style == 'unicode':
            self.piece_style_combo.setCurrentIndex(0)
        else:
            self.piece_style_combo.setCurrentIndex(1)
        self.piece_style_combo.setStyleSheet("""
            QComboBox {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 6px;
            }
        """)
        pieces_layout.addRow("Style:", self.piece_style_combo)
        
        layout.addWidget(pieces_group)
        
        # Display options group
        display_group = QGroupBox("Options d'Affichage")
        display_layout = QFormLayout(display_group)
        
        self.show_coords_check = QCheckBox("Afficher les coordonnées (a-h, 1-8)")
        self.show_coords_check.setChecked(self.temp_config['show_coordinates'])
        self.show_coords_check.setStyleSheet("color: #d4d4d4;")
        display_layout.addRow(self.show_coords_check)
        
        self.show_legal_check = QCheckBox("Afficher les coups légaux")
        self.show_legal_check.setChecked(self.temp_config['show_legal_moves'])
        self.show_legal_check.setStyleSheet("color: #d4d4d4;")
        display_layout.addRow(self.show_legal_check)
        
        # Square size
        size_layout = QHBoxLayout()
        self.size_spin = QSpinBox()
        self.size_spin.setRange(50, 120)
        self.size_spin.setValue(self.temp_config['square_size'])
        self.size_spin.setSuffix(" px")
        self.size_spin.setStyleSheet("""
            QSpinBox {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        size_layout.addWidget(self.size_spin)
        size_layout.addStretch()
        display_layout.addRow("Taille des cases:", size_layout)
        
        layout.addWidget(display_group)
        
        # Sound options group
        sound_group = QGroupBox("Sons")
        sound_layout = QFormLayout(sound_group)
        
        self.sounds_enabled_check = QCheckBox("Activer les sons")
        self.sounds_enabled_check.setChecked(self.temp_config['sounds_enabled'])
        self.sounds_enabled_check.setStyleSheet("color: #d4d4d4;")
        self.sounds_enabled_check.stateChanged.connect(self.on_sounds_toggled)
        sound_layout.addRow(self.sounds_enabled_check)
        
        # Volume slider
        volume_layout = QHBoxLayout()
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.temp_config['sound_volume'] * 100))
        self.volume_slider.setEnabled(self.temp_config['sounds_enabled'])
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #3e3e3e;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0e639c;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel(f"{int(self.temp_config['sound_volume'] * 100)}%")
        self.volume_label.setMinimumWidth(40)
        volume_layout.addWidget(self.volume_label)
        sound_layout.addRow("Volume:", volume_layout)
        
        layout.addWidget(sound_group)
        
        # Preset themes
        themes_group = QGroupBox("Thèmes Prédéfinis")
        themes_layout = QHBoxLayout(themes_group)
        
        classic_button = QPushButton("🟫 Classique")
        classic_button.clicked.connect(lambda: self.apply_preset('classic'))
        themes_layout.addWidget(classic_button)
        
        blue_button = QPushButton("🔵 Bleu")
        blue_button.clicked.connect(lambda: self.apply_preset('blue'))
        themes_layout.addWidget(blue_button)
        
        green_button = QPushButton("🟢 Vert")
        green_button.clicked.connect(lambda: self.apply_preset('green'))
        themes_layout.addWidget(green_button)
        
        layout.addWidget(themes_group)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        reset_button = QPushButton("Réinitialiser")
        reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_button)
        
        button_layout.addStretch()
        
        apply_button = QPushButton("✔ Appliquer")
        apply_button.setMinimumWidth(100)
        apply_button.clicked.connect(self.apply_config)
        button_layout.addWidget(apply_button)
        
        cancel_button = QPushButton("Annuler")
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
    def choose_color(self, config_key: str, preview_label: QLabel):
        """Open color chooser dialog"""
        current_color = QColor(self.temp_config[config_key])
        color = QColorDialog.getColor(current_color, self, "Choisir une couleur")
        
        if color.isValid():
            self.temp_config[config_key] = color.name()
            preview_label.setStyleSheet(
                f"background-color: {color.name()}; "
                "border: 1px solid #3e3e3e; border-radius: 4px;"
            )
            
    def on_sounds_toggled(self, state):
        """Handle sounds enabled checkbox"""
        enabled = (state == Qt.CheckState.Checked.value)
        self.volume_slider.setEnabled(enabled)
        
    def on_volume_changed(self, value):
        """Handle volume slider change"""
        self.volume_label.setText(f"{value}%")
        
    def apply_preset(self, preset: str):
        """Apply a preset theme"""
        presets = {
            'classic': {
                'light_square_color': '#f0d9b5',
                'dark_square_color': '#b58863',
                'highlight_color': '#646f40',
            },
            'blue': {
                'light_square_color': '#dee3e6',
                'dark_square_color': '#8ca2ad',
                'highlight_color': '#4a90a4',
            },
            'green': {
                'light_square_color': '#ffffdd',
                'dark_square_color': '#86a666',
                'highlight_color': '#4b8a3c',
            }
        }
        
        if preset in presets:
            self.temp_config.update(presets[preset])
            # Update preview labels
            self.light_square_preview.setStyleSheet(
                f"background-color: {self.temp_config['light_square_color']}; "
                "border: 1px solid #3e3e3e; border-radius: 4px;"
            )
            self.dark_square_preview.setStyleSheet(
                f"background-color: {self.temp_config['dark_square_color']}; "
                "border: 1px solid #3e3e3e; border-radius: 4px;"
            )
            self.highlight_preview.setStyleSheet(
                f"background-color: {self.temp_config['highlight_color']}; "
                "border: 1px solid #3e3e3e; border-radius: 4px;"
            )
            
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.temp_config = BoardConfig.DEFAULT_CONFIG.copy()
        # Update all UI elements
        self.light_square_preview.setStyleSheet(
            f"background-color: {self.temp_config['light_square_color']}; "
            "border: 1px solid #3e3e3e; border-radius: 4px;"
        )
        self.dark_square_preview.setStyleSheet(
            f"background-color: {self.temp_config['dark_square_color']}; "
            "border: 1px solid #3e3e3e; border-radius: 4px;"
        )
        self.highlight_preview.setStyleSheet(
            f"background-color: {self.temp_config['highlight_color']}; "
            "border: 1px solid #3e3e3e; border-radius: 4px;"
        )
        self.piece_style_combo.setCurrentIndex(0)
        self.show_coords_check.setChecked(True)
        self.show_legal_check.setChecked(True)
        self.size_spin.setValue(70)
        self.sounds_enabled_check.setChecked(True)
        self.volume_slider.setValue(70)
        
    def apply_config(self):
        """Apply configuration"""
        # Update temp config from UI
        self.temp_config['piece_style'] = 'unicode' if self.piece_style_combo.currentIndex() == 0 else 'ascii'
        self.temp_config['show_coordinates'] = self.show_coords_check.isChecked()
        self.temp_config['show_legal_moves'] = self.show_legal_check.isChecked()
        self.temp_config['square_size'] = self.size_spin.value()
        self.temp_config['sounds_enabled'] = self.sounds_enabled_check.isChecked()
        self.temp_config['sound_volume'] = self.volume_slider.value() / 100.0
        
        # Update board config
        self.board_config.config = self.temp_config.copy()
        self.board_config.save()
        
        # Emit signal
        self.config_changed.emit(self.temp_config)
        
        self.accept()

