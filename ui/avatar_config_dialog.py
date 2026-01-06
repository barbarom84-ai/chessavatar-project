"""
Avatar Configuration Dialog - Customize avatar behavior and strength
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSlider, QGroupBox, QFormLayout,
                             QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from pathlib import Path
from typing import Optional

from core.avatar_manager import Avatar, AvatarManager


class AvatarConfigDialog(QDialog):
    """Dialog for configuring avatar parameters"""
    
    def __init__(self, avatar: Avatar, avatar_manager: AvatarManager, parent=None):
        super().__init__(parent)
        self.avatar = avatar
        self.avatar_manager = avatar_manager
        self.init_ui()
        self.apply_theme()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Configuration de l'Avatar")
        self.setModal(True)
        self.setMinimumSize(600, 700)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header with avatar info
        header_layout = QHBoxLayout()
        
        # Photo
        photo_label = QLabel()
        photo_label.setFixedSize(100, 100)
        photo_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 2px solid #3e3e3e;
                border-radius: 8px;
            }
        """)
        photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo_label.setScaledContents(True)
        
        if self.avatar.photo_path and Path(self.avatar.photo_path).exists():
            pixmap = QPixmap(self.avatar.photo_path)
            photo_label.setPixmap(pixmap)
        else:
            photo_label.setText("👤")
            photo_label.setStyleSheet(photo_label.styleSheet() + "font-size: 48pt;")
        
        header_layout.addWidget(photo_label)
        
        # Info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(self.avatar.display_name)
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setBold(True)
        name_label.setFont(name_font)
        info_layout.addWidget(name_label)
        
        platform_label = QLabel(f"🌐 {self.avatar.platform.title()}")
        platform_label.setStyleSheet("font-size: 11pt; color: #888888;")
        info_layout.addWidget(platform_label)
        
        # Stats
        style_data = self.avatar.style_data
        elo = style_data.get('average_elo', 1500)
        win_rate = style_data.get('win_rate', 0) * 100
        total_games = style_data.get('total_games', 0)
        
        stats_label = QLabel(f"📊 Elo: {elo} • Victoires: {win_rate:.0f}% • {total_games} parties")
        stats_label.setStyleSheet("font-size: 10pt; color: #888888;")
        info_layout.addWidget(stats_label)
        
        # Play style
        play_style = style_data.get('play_style', 'Équilibré')
        style_label = QLabel(f"🎯 Style: {play_style}")
        style_label.setStyleSheet("font-size: 10pt; color: #888888;")
        info_layout.addWidget(style_label)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout, stretch=1)
        
        layout.addLayout(header_layout)
        
        # Separator
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #3e3e3e;")
        layout.addWidget(separator)
        
        # Configuration section
        config_group = QGroupBox("⚙️ Configuration du moteur")
        config_layout = QFormLayout(config_group)
        config_layout.setSpacing(15)
        
        # Skill Level
        self.skill_level_spin = QSpinBox()
        self.skill_level_spin.setRange(-1, 20)
        self.skill_level_spin.setValue(-1)
        self.skill_level_spin.setSpecialValueText("Auto (basé sur Elo)")
        self.skill_level_spin.setToolTip("Niveau de jeu (0=débutant, 20=expert)")
        self.skill_level_spin.setMinimumHeight(35)
        self.skill_level_spin.setMinimumWidth(200)
        self.skill_level_spin.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)
        config_layout.addRow("Skill Level:", self.skill_level_spin)
        
        # Time per move (seconds)
        time_layout = QHBoxLayout()
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(5, 50)  # 0.5s to 5.0s (in 0.1s steps)
        self.time_slider.setValue(20)  # 2.0s default
        self.time_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.time_slider.setTickInterval(5)
        self.time_slider.setMinimumHeight(30)
        self.time_label = QLabel("2.0s")
        self.time_label.setMinimumWidth(50)
        self.time_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        self.time_slider.valueChanged.connect(
            lambda v: self.time_label.setText(f"{v/10:.1f}s")
        )
        time_layout.addWidget(self.time_slider, stretch=1)
        time_layout.addWidget(self.time_label)
        config_layout.addRow("Temps de réflexion:", time_layout)
        
        # Error rate (variance)
        variance_layout = QHBoxLayout()
        self.variance_slider = QSlider(Qt.Orientation.Horizontal)
        self.variance_slider.setRange(0, 50)  # 0% to 50%
        self.variance_slider.setValue(10)  # 10% default
        self.variance_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.variance_slider.setTickInterval(10)
        self.variance_slider.setMinimumHeight(30)
        self.variance_label = QLabel("10%")
        self.variance_label.setMinimumWidth(50)
        self.variance_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        self.variance_slider.valueChanged.connect(
            lambda v: self.variance_label.setText(f"{v}%")
        )
        variance_layout.addWidget(self.variance_slider, stretch=1)
        variance_layout.addWidget(self.variance_label)
        config_layout.addRow("Variance (erreurs):", variance_layout)
        
        # Depth limit
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(1, 30)
        self.depth_spin.setValue(12)
        self.depth_spin.setToolTip("Profondeur de recherche (1=très faible, 30=très fort)")
        self.depth_spin.setMinimumHeight(35)
        self.depth_spin.setMinimumWidth(200)
        self.depth_spin.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)
        config_layout.addRow("Profondeur max:", self.depth_spin)
        
        layout.addWidget(config_group)
        
        # Opening preferences (display only)
        opening_group = QGroupBox("📖 Ouvertures favorites")
        opening_layout = QVBoxLayout(opening_group)
        
        top_openings_white = style_data.get('top_openings_white', [])
        top_openings_black = style_data.get('top_openings_black', [])
        
        if top_openings_white:
            white_label = QLabel("Avec les Blancs:")
            white_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
            opening_layout.addWidget(white_label)
            
            for opening, count in top_openings_white[:3]:
                opening_item = QLabel(f"  • {opening} ({count} parties)")
                opening_item.setStyleSheet("font-size: 9pt; color: #888888;")
                opening_layout.addWidget(opening_item)
        
        if top_openings_black:
            black_label = QLabel("Avec les Noirs:")
            black_label.setStyleSheet("font-weight: bold; font-size: 10pt; margin-top: 5px;")
            opening_layout.addWidget(black_label)
            
            for opening, count in top_openings_black[:3]:
                opening_item = QLabel(f"  • {opening} ({count} parties)")
                opening_item.setStyleSheet("font-size: 9pt; color: #888888;")
                opening_layout.addWidget(opening_item)
        
        if not top_openings_white and not top_openings_black:
            no_openings = QLabel("Aucune donnée d'ouverture disponible")
            no_openings.setStyleSheet("font-size: 9pt; color: #888888; font-style: italic;")
            opening_layout.addWidget(no_openings)
        
        layout.addWidget(opening_group)
        
        # Info note
        note = QLabel(
            "💡 Note: Ces paramètres affectent la force et le comportement de l'avatar.\n"
            "Un Skill Level de -1 utilise la force calculée automatiquement à partir du profil."
        )
        note.setStyleSheet("color: #888888; font-size: 9pt; font-style: italic;")
        note.setWordWrap(True)
        layout.addWidget(note)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        reset_btn = QPushButton("Réinitialiser")
        reset_btn.setMinimumHeight(35)
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setMinimumHeight(35)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Sauvegarder")
        save_btn.setMinimumHeight(35)
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Load current config if exists
        self.load_current_config()
    
    def load_current_config(self):
        """Load current avatar configuration"""
        # For now, config is stored in style_data
        # In a real implementation, you'd have a separate config storage
        config = self.avatar.style_data.get('custom_config', {})
        
        if 'skill_level' in config:
            self.skill_level_spin.setValue(config['skill_level'])
        
        if 'time_limit' in config:
            self.time_slider.setValue(int(config['time_limit'] * 10))
        
        if 'variance' in config:
            self.variance_slider.setValue(int(config['variance']))
        
        if 'depth' in config:
            self.depth_spin.setValue(config['depth'])
    
    def reset_to_defaults(self):
        """Reset to default values"""
        self.skill_level_spin.setValue(-1)
        self.time_slider.setValue(20)  # 2.0s
        self.variance_slider.setValue(10)  # 10%
        self.depth_spin.setValue(12)
    
    def save_config(self):
        """Save configuration"""
        config = {
            'skill_level': self.skill_level_spin.value(),
            'time_limit': self.time_slider.value() / 10.0,
            'variance': self.variance_slider.value(),
            'depth': self.depth_spin.value()
        }
        
        # Store in avatar's style_data
        self.avatar.style_data['custom_config'] = config
        
        # Save to disk
        if self.avatar_manager.save_avatars():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Succès",
                f"Configuration de '{self.avatar.display_name}' sauvegardée!\n\n"
                "Les changements seront appliqués à la prochaine partie."
            )
            self.accept()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Erreur",
                "Impossible de sauvegarder la configuration."
            )
    
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
            QLabel {
                color: #d4d4d4;
            }
            QSpinBox {
                background-color: #252526;
                color: #d4d4d4;
                border: 2px solid #3e3e3e;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 11pt;
                font-weight: bold;
            }
            QSpinBox:hover {
                border: 2px solid #0e639c;
                background-color: #2d2d2d;
            }
            QSpinBox:focus {
                border: 2px solid #1177bb;
                background-color: #2d2d2d;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 25px;
                height: 15px;
                border-left: 1px solid #3e3e3e;
                background-color: #1e1e1e;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #0e639c;
            }
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
                background-color: #0d5689;
            }
            QSpinBox::up-arrow {
                image: none;
                border: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 6px solid #d4d4d4;
            }
            QSpinBox::down-arrow {
                image: none;
                border: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #d4d4d4;
            }
            QSlider::groove:horizontal {
                background: #3e3e3e;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1177bb, stop:1 #0e639c);
                width: 20px;
                height: 20px;
                margin: -6px 0;
                border-radius: 10px;
                border: 2px solid #0d5689;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a8dd1, stop:1 #1177bb);
                border: 2px solid #1177bb;
            }
            QSlider::handle:horizontal:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0e639c, stop:1 #0a4f7d);
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0e639c, stop:1 #1177bb);
                border-radius: 4px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 25px;
                font-size: 11pt;
                font-weight: bold;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5689;
            }
        """)

