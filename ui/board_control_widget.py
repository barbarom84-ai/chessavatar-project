"""
Board Control Widget - Zoom and Pan Controls for Chessboard
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QSlider, QGroupBox, QToolButton)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon


class BoardControlWidget(QWidget):
    """Widget with zoom and pan controls for chessboard"""
    
    # Signals
    zoom_in_clicked = pyqtSignal()
    zoom_out_clicked = pyqtSignal()
    zoom_reset_clicked = pyqtSignal()
    zoom_changed = pyqtSignal(float)
    pan_mode_toggled = pyqtSignal(bool)
    pan_reset_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        
        # Group box for controls
        control_group = QGroupBox("🎮 Contrôles de l'Échiquier")
        control_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #FFA726;
                border: 2px solid #FFA726;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 15px;
                padding-bottom: 10px;
                background-color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                background-color: #2b2b2b;
            }
        """)
        
        group_layout = QVBoxLayout(control_group)
        group_layout.setSpacing(12)
        
        # Zoom section
        zoom_label = QLabel("🔍 Zoom")
        zoom_label.setStyleSheet("font-size: 10pt; color: #FFA726; font-weight: bold;")
        group_layout.addWidget(zoom_label)
        
        # Zoom buttons row
        zoom_buttons_layout = QHBoxLayout()
        zoom_buttons_layout.setSpacing(8)
        
        btn_style = """
            QPushButton {
                background-color: #2e2e2e;
                color: #d4d4d4;
                border: 2px solid #FFA726;
                border-radius: 4px;
                min-width: 35px;
                min-height: 35px;
                font-size: 16pt;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #FFA726;
                color: #1e1e1e;
            }
            QPushButton:pressed {
                background-color: #FF8F00;
            }
        """
        
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.setStyleSheet(btn_style)
        self.zoom_out_btn.setToolTip("Dézoomer (Molette souris vers bas)")
        self.zoom_out_btn.clicked.connect(self.zoom_out_clicked.emit)
        zoom_buttons_layout.addWidget(self.zoom_out_btn)
        
        self.zoom_reset_btn = QPushButton("⌂")
        self.zoom_reset_btn.setStyleSheet(btn_style.replace("35px", "40px"))
        self.zoom_reset_btn.setToolTip("Réinitialiser zoom (100%)")
        self.zoom_reset_btn.clicked.connect(self.zoom_reset_clicked.emit)
        zoom_buttons_layout.addWidget(self.zoom_reset_btn)
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setStyleSheet(btn_style)
        self.zoom_in_btn.setToolTip("Zoomer (Molette souris vers haut)")
        self.zoom_in_btn.clicked.connect(self.zoom_in_clicked.emit)
        zoom_buttons_layout.addWidget(self.zoom_in_btn)
        
        zoom_buttons_layout.addStretch()
        group_layout.addLayout(zoom_buttons_layout)
        
        # Zoom slider
        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(8)
        
        slider_label_min = QLabel("50%")
        slider_label_min.setStyleSheet("font-size: 9pt; color: #888888;")
        slider_layout.addWidget(slider_label_min)
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(50)  # 50%
        self.zoom_slider.setMaximum(200)  # 200%
        self.zoom_slider.setValue(100)  # 100%
        self.zoom_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.zoom_slider.setTickInterval(25)
        self.zoom_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #3e3e3e;
                height: 6px;
                background: #2e2e2e;
                margin: 2px 0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #FFA726;
                border: 2px solid #FF8F00;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #FFB74D;
            }
        """)
        self.zoom_slider.valueChanged.connect(self._on_slider_changed)
        slider_layout.addWidget(self.zoom_slider)
        
        slider_label_max = QLabel("200%")
        slider_label_max.setStyleSheet("font-size: 9pt; color: #888888;")
        slider_layout.addWidget(slider_label_max)
        
        group_layout.addLayout(slider_layout)
        
        # Current zoom display
        self.zoom_display = QLabel("Zoom: 100%")
        self.zoom_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_display.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                color: #FFA726;
                font-weight: bold;
                padding: 4px 8px;
                background-color: #0e1e2e;
                border: 1px solid #FFA726;
                border-radius: 4px;
            }
        """)
        group_layout.addWidget(self.zoom_display)
        
        # Separator
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #3e3e3e; margin: 5px 0;")
        group_layout.addWidget(separator)
        
        # Pan section
        pan_label = QLabel("🖐️ Déplacement")
        pan_label.setStyleSheet("font-size: 10pt; color: #FFA726; font-weight: bold;")
        group_layout.addWidget(pan_label)
        
        # Pan toggle button
        pan_buttons_layout = QHBoxLayout()
        pan_buttons_layout.setSpacing(8)
        
        toggle_style = """
            QPushButton {
                background-color: #2e2e2e;
                color: #d4d4d4;
                border: 2px solid #FFA726;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3e3e3e;
                border-color: #FFB74D;
            }
            QPushButton:checked {
                background-color: #FFA726;
                color: #1e1e1e;
                border-color: #FF8F00;
            }
        """
        
        self.pan_toggle_btn = QPushButton("🖐️ Mode Déplacement")
        self.pan_toggle_btn.setCheckable(True)
        self.pan_toggle_btn.setStyleSheet(toggle_style)
        self.pan_toggle_btn.setToolTip("Activer/Désactiver le mode déplacement\n(Cliquez et faites glisser l'échiquier)")
        self.pan_toggle_btn.toggled.connect(self._on_pan_toggled)
        pan_buttons_layout.addWidget(self.pan_toggle_btn)
        
        self.pan_reset_btn = QPushButton("↺")
        self.pan_reset_btn.setStyleSheet(btn_style)
        self.pan_reset_btn.setToolTip("Recentrer l'échiquier")
        self.pan_reset_btn.clicked.connect(self.pan_reset_clicked.emit)
        pan_buttons_layout.addWidget(self.pan_reset_btn)
        
        pan_buttons_layout.addStretch()
        group_layout.addLayout(pan_buttons_layout)
        
        # Info label
        info_label = QLabel("💡 Utilisez la molette de la souris pour zoomer !")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 9pt; color: #888888; font-style: italic;")
        group_layout.addWidget(info_label)
        
        main_layout.addWidget(control_group)
        main_layout.addStretch()
    
    def _on_slider_changed(self, value: int):
        """Handle slider value change"""
        zoom = value / 100.0
        self.zoom_changed.emit(zoom)
    
    def _on_pan_toggled(self, checked: bool):
        """Handle pan mode toggle"""
        if checked:
            self.pan_toggle_btn.setText("🎮 Mode Jeu")
            self.pan_toggle_btn.setToolTip("Retour au mode de jeu normal")
        else:
            self.pan_toggle_btn.setText("🖐️ Mode Déplacement")
            self.pan_toggle_btn.setToolTip("Activer/Désactiver le mode déplacement\n(Cliquez et faites glisser l'échiquier)")
        self.pan_mode_toggled.emit(checked)
    
    def update_zoom_display(self, zoom: float):
        """Update the zoom percentage display"""
        percentage = int(zoom * 100)
        self.zoom_display.setText(f"Zoom: {percentage}%")
        # Update slider without triggering signal
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(percentage)
        self.zoom_slider.blockSignals(False)
    
    def set_pan_mode(self, enabled: bool):
        """Set pan mode state"""
        self.pan_toggle_btn.setChecked(enabled)

