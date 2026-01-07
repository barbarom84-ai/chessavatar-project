"""
WinBoard Engine Configuration Dialog
For configuring WinBoard-specific settings like strength/ELO for TheKing
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSlider, QSpinBox, QGroupBox,
                             QFormLayout, QComboBox, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class WinboardEngineConfigDialog(QDialog):
    """Dialog for configuring WinBoard engine settings"""
    
    def __init__(self, engine_name: str, current_settings: dict = None, parent=None):
        super().__init__(parent)
        self.engine_name = engine_name
        self.settings = current_settings or {}
        
        self.init_ui()
        self.apply_theme()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle(f"Configuration {self.engine_name}")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel(f"Réglages du moteur {self.engine_name}")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Strength/ELO Group (for TheKing engines)
        if "king" in self.engine_name.lower():
            strength_group = QGroupBox("Force de jeu")
            strength_layout = QVBoxLayout()
            
            # ELO/Depth slider
            elo_layout = QHBoxLayout()
            elo_label = QLabel("Niveau (profondeur):")
            elo_layout.addWidget(elo_label)
            
            self.depth_slider = QSlider(Qt.Orientation.Horizontal)
            self.depth_slider.setMinimum(1)
            self.depth_slider.setMaximum(20)
            self.depth_slider.setValue(self.settings.get('depth', 10))
            self.depth_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            self.depth_slider.setTickInterval(2)
            self.depth_slider.valueChanged.connect(self.on_depth_changed)
            elo_layout.addWidget(self.depth_slider)
            
            self.depth_label = QLabel(f"{self.depth_slider.value()}")
            self.depth_label.setMinimumWidth(30)
            elo_layout.addWidget(self.depth_label)
            
            strength_layout.addLayout(elo_layout)
            
            # Indication levels
            indicator_label = QLabel(
                "Niveaux indicatifs:\n"
                "1-5: Débutant (800-1200 ELO)\n"
                "6-10: Intermédiaire (1200-1800 ELO)\n"
                "11-15: Avancé (1800-2200 ELO)\n"
                "16-20: Expert (2200+ ELO)"
            )
            indicator_label.setStyleSheet("color: #888; font-size: 9pt; padding: 5px;")
            strength_layout.addWidget(indicator_label)
            
            strength_group.setLayout(strength_layout)
            layout.addWidget(strength_group)
        
        # Time control settings
        time_group = QGroupBox("Contrôle du temps")
        time_layout = QFormLayout()
        
        self.time_per_move_spin = QSpinBox()
        self.time_per_move_spin.setMinimum(1)
        self.time_per_move_spin.setMaximum(300)
        self.time_per_move_spin.setValue(self.settings.get('time_per_move', 5))
        self.time_per_move_spin.setSuffix(" sec")
        time_layout.addRow("Temps par coup:", self.time_per_move_spin)
        
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        # Advanced options (if any)
        advanced_group = QGroupBox("Options avancées")
        advanced_layout = QFormLayout()
        
        # Random/Variety
        self.random_check = QCheckBox("Activer la variété des coups")
        self.random_check.setChecked(self.settings.get('random', True))
        advanced_layout.addRow("", self.random_check)
        
        # Ponder (think on opponent's time)
        self.ponder_check = QCheckBox("Réfléchir pendant le tour adverse")
        self.ponder_check.setChecked(self.settings.get('ponder', False))
        advanced_layout.addRow("", self.ponder_check)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        # Info label
        info_label = QLabel(
            "Note: Ces paramètres s'appliquent spécifiquement aux moteurs WinBoard.\n"
            "Pour les moteurs UCI, utilisez la configuration UCI standard."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #4FC3F7; font-size: 9pt; padding: 10px; background: #1a1a1a; border-radius: 5px;")
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("Appliquer")
        ok_btn.setMinimumWidth(100)
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_depth_changed(self, value):
        """Update depth label"""
        self.depth_label.setText(str(value))
    
    def get_settings(self) -> dict:
        """Get configured settings"""
        settings = {
            'time_per_move': self.time_per_move_spin.value(),
            'random': self.random_check.isChecked(),
            'ponder': self.ponder_check.isChecked()
        }
        
        # Add depth for TheKing engines
        if hasattr(self, 'depth_slider'):
            settings['depth'] = self.depth_slider.value()
        
        return settings
    
    def apply_theme(self):
        """Apply dark theme"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: #4FC3F7;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #555555;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4FC3F7;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #6FD8FF;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: 1px solid #555555;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
                border: 1px solid #4FC3F7;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
            QPushButton:default {
                background-color: #0d7ea2;
                border: 1px solid #4FC3F7;
            }
            QPushButton:default:hover {
                background-color: #1a8bb5;
            }
            QSpinBox, QComboBox {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QCheckBox {
                color: #e0e0e0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #3d3d3d;
            }
            QCheckBox::indicator:checked {
                background-color: #4FC3F7;
                border-color: #4FC3F7;
            }
        """)

