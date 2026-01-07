"""
Chessmaster Theme Selector Dialog
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QListWidget, QListWidgetItem, QGroupBox,
                              QScrollArea, QWidget, QComboBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage
import os

from core.chessmaster_themes import get_chessmaster_theme_manager


class ChessmasterThemeDialog(QDialog):
    """Dialog for selecting Chessmaster themes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = get_chessmaster_theme_manager()
        self.selected_theme_id = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Thèmes Chessmaster")
        self.setMinimumSize(900, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("🎨 Collection de Thèmes Chessmaster")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #4FC3F7;")
        layout.addWidget(title)
        
        # Info label
        info = QLabel(f"55 thèmes disponibles (Bois, Métal, Verre, Historiques, Cartoon, et plus)")
        info.setStyleSheet("color: #888888; font-size: 10pt;")
        layout.addWidget(info)
        
        # Main content (horizontal split)
        content_layout = QHBoxLayout()
        
        # Left: Category filter and theme list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Category filter
        filter_label = QLabel("Catégorie:")
        filter_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(filter_label)
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("Tous", "all")
        self.category_combo.addItem("🪵 Bois (4)", "wood")
        self.category_combo.addItem("🔩 Métal (6)", "metal")
        self.category_combo.addItem("💎 Verre (6)", "glass")
        self.category_combo.addItem("🗿 Marbre/Céramique (4)", "marble")
        self.category_combo.addItem("🏛️ Historiques (13)", "historic")
        self.category_combo.addItem("🎨 Modernes (4)", "modern")
        self.category_combo.addItem("🎭 Cartoon (5)", "cartoon")
        self.category_combo.addItem("📏 2D/Plats (11)", "2d")
        self.category_combo.addItem("👑 Staunton Officiels (2)", "staunton")
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        left_layout.addWidget(self.category_combo)
        
        # Theme list
        self.theme_list = QListWidget()
        self.theme_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2e2e2e;
            }
            QListWidget::item:selected {
                background-color: #4FC3F7;
                color: #1e1e1e;
            }
            QListWidget::item:hover {
                background-color: #2e2e2e;
            }
        """)
        self.theme_list.currentItemChanged.connect(self._on_theme_selected)
        left_layout.addWidget(self.theme_list)
        
        left_panel.setMaximumWidth(350)
        content_layout.addWidget(left_panel)
        
        # Right: Preview and details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Theme name
        self.theme_name_label = QLabel("Sélectionnez un thème")
        self.theme_name_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #d4d4d4;")
        right_layout.addWidget(self.theme_name_label)
        
        # Theme description
        self.theme_desc_label = QLabel("")
        self.theme_desc_label.setStyleSheet("color: #888888; font-size: 10pt;")
        self.theme_desc_label.setWordWrap(True)
        right_layout.addWidget(self.theme_desc_label)
        
        # Preview image
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #1e1e1e; border: 2px solid #3e3e3e; border-radius: 4px;")
        self.preview_label.setMinimumSize(400, 400)
        right_layout.addWidget(self.preview_label, stretch=1)
        
        content_layout.addWidget(right_panel, stretch=1)
        
        layout.addLayout(content_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3e3e3e;
                color: #d4d4d4;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #4e4e4e;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("Appliquer")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4FC3F7;
                color: #1e1e1e;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6FD3F7;
            }
        """)
        apply_btn.clicked.connect(self.accept)
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
        
        # Load themes
        self._load_themes()
    
    def _load_themes(self, category: str = "all"):
        """Load themes into list"""
        self.theme_list.clear()
        
        if category == "all":
            themes = self.theme_manager.get_available_themes()
        else:
            themes = self.theme_manager.get_themes_by_category(category)
        
        # Sort by name
        themes = sorted(themes, key=lambda t: t.name)
        
        for theme in themes:
            item = QListWidgetItem(f"{theme.name}")
            item.setData(Qt.ItemDataRole.UserRole, theme.id)
            self.theme_list.addItem(item)
        
        # Select first item
        if self.theme_list.count() > 0:
            self.theme_list.setCurrentRow(0)
    
    def _on_category_changed(self, index: int):
        """Handle category change"""
        category = self.category_combo.itemData(index)
        self._load_themes(category)
    
    def _on_theme_selected(self, current, previous):
        """Handle theme selection"""
        if not current:
            return
        
        theme_id = current.data(Qt.ItemDataRole.UserRole)
        theme = self.theme_manager.get_theme(theme_id)
        
        if not theme:
            return
        
        self.selected_theme_id = theme_id
        
        # Update name and description
        self.theme_name_label.setText(theme.name)
        self.theme_desc_label.setText(theme.description)
        
        # Load preview image
        preview_path = self.theme_manager.get_preview_path(theme_id)
        if preview_path and os.path.exists(preview_path):
            pixmap = QPixmap(preview_path)
            # Scale to fit
            scaled = pixmap.scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio, 
                                  Qt.TransformationMode.SmoothTransformation)
            self.preview_label.setPixmap(scaled)
        else:
            self.preview_label.setText("Aperçu non disponible")
    
    def get_selected_theme(self) -> str:
        """Get selected theme ID"""
        return self.selected_theme_id

