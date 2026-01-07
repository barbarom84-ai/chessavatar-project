"""
Layout Configuration Dialog
Allows users to select, create, and manage UI layouts
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QListWidget, QListWidgetItem, QPushButton, QLabel,
                             QMessageBox, QInputDialog, QFileDialog, QTextEdit,
                             QCheckBox, QGridLayout, QSlider, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ui.layout_manager import LayoutManager, LayoutConfig
from ui.styles import get_button_style, COLORS, FONTS


class LayoutConfigDialog(QDialog):
    """Dialog for managing UI layouts"""
    
    layout_changed = pyqtSignal(LayoutConfig)
    
    def __init__(self, layout_manager: LayoutManager, parent=None):
        super().__init__(parent)
        self.layout_manager = layout_manager
        self.current_layout = layout_manager.get_current_layout()
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("🎨 Disposition de l'Interface")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🎨 Personnalisation de la Disposition")
        title.setStyleSheet(f"{FONTS['title']} color: {COLORS['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Choisissez une disposition prédéfinie ou créez la vôtre")
        desc.setStyleSheet(f"color: {COLORS['text_secondary']}; padding: 5px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Main content
        content_layout = QHBoxLayout()
        
        # Left: Layout list
        left_group = QGroupBox("📋 Dispositions Disponibles")
        left_layout = QVBoxLayout()
        
        self.layout_list = QListWidget()
        self.layout_list.itemClicked.connect(self.on_layout_selected)
        self.populate_layout_list()
        left_layout.addWidget(self.layout_list)
        
        # Buttons for layout management
        list_buttons = QHBoxLayout()
        
        self.btn_new = QPushButton("➕ Nouvelle")
        self.btn_new.clicked.connect(self.create_new_layout)
        self.btn_new.setStyleSheet(get_button_style('primary'))
        list_buttons.addWidget(self.btn_new)
        
        self.btn_delete = QPushButton("🗑️ Supprimer")
        self.btn_delete.clicked.connect(self.delete_layout)
        self.btn_delete.setStyleSheet(get_button_style('danger'))
        list_buttons.addWidget(self.btn_delete)
        
        self.btn_export = QPushButton("💾 Exporter")
        self.btn_export.clicked.connect(self.export_layout)
        list_buttons.addWidget(self.btn_export)
        
        self.btn_import = QPushButton("📂 Importer")
        self.btn_import.clicked.connect(self.import_layout)
        list_buttons.addWidget(self.btn_import)
        
        left_layout.addLayout(list_buttons)
        left_group.setLayout(left_layout)
        content_layout.addWidget(left_group, stretch=1)
        
        # Right: Layout preview and options
        right_group = QGroupBox("⚙️ Options de Disposition")
        right_layout = QVBoxLayout()
        
        # Panel visibility
        panels_group = QGroupBox("👁️ Panels Visibles")
        panels_layout = QGridLayout()
        
        self.panel_checks = {}
        panels = [
            ('engine', '⚙️ Moteur d\'Analyse'),
            ('opening', '📖 Ouvertures'),
            ('notation', '📋 Notation PGN'),
            ('clock', '⏱️ Pendule'),
            ('avatar_status', '🤖 Statut Avatar'),
            ('game_controls', '🎮 Contrôles de Jeu'),
        ]
        
        row = 0
        col = 0
        for key, label in panels:
            check = QCheckBox(label)
            check.setChecked(self.current_layout.panels_visible.get(key, True))
            check.stateChanged.connect(lambda state, k=key: self.on_panel_visibility_changed(k, state))
            self.panel_checks[key] = check
            panels_layout.addWidget(check, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        panels_group.setLayout(panels_layout)
        right_layout.addWidget(panels_group)
        
        # Splitter sizes
        splitter_group = QGroupBox("📐 Tailles des Panels")
        splitter_layout = QVBoxLayout()
        
        # Left/Right ratio
        ratio_layout = QHBoxLayout()
        ratio_layout.addWidget(QLabel("Échiquier vs Panneau Droit:"))
        
        self.splitter_slider = QSlider(Qt.Orientation.Horizontal)
        self.splitter_slider.setMinimum(50)
        self.splitter_slider.setMaximum(90)
        left_percent = int((self.current_layout.splitter_sizes[0] / sum(self.current_layout.splitter_sizes)) * 100)
        self.splitter_slider.setValue(left_percent)
        self.splitter_slider.valueChanged.connect(self.on_splitter_changed)
        ratio_layout.addWidget(self.splitter_slider)
        
        self.splitter_label = QLabel(f"{left_percent}% / {100-left_percent}%")
        ratio_layout.addWidget(self.splitter_label)
        
        splitter_layout.addLayout(ratio_layout)
        splitter_group.setLayout(splitter_layout)
        right_layout.addWidget(splitter_group)
        
        # Description area
        desc_group = QGroupBox("ℹ️ Description")
        desc_layout = QVBoxLayout()
        
        self.desc_text = QTextEdit()
        self.desc_text.setMaximumHeight(100)
        self.desc_text.setReadOnly(True)
        self.update_description()
        desc_layout.addWidget(self.desc_text)
        
        desc_group.setLayout(desc_layout)
        right_layout.addWidget(desc_group)
        
        right_layout.addStretch()
        right_group.setLayout(right_layout)
        content_layout.addWidget(right_group, stretch=1)
        
        layout.addLayout(content_layout)
        
        # Bottom buttons
        buttons_layout = QHBoxLayout()
        
        self.btn_preview = QPushButton("👁️ Aperçu")
        self.btn_preview.clicked.connect(self.preview_layout)
        self.btn_preview.setStyleSheet(get_button_style('primary'))
        buttons_layout.addWidget(self.btn_preview)
        
        buttons_layout.addStretch()
        
        self.btn_cancel = QPushButton("❌ Annuler")
        self.btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_cancel)
        
        self.btn_apply = QPushButton("✅ Appliquer")
        self.btn_apply.clicked.connect(self.apply_layout)
        self.btn_apply.setStyleSheet(get_button_style('success'))
        buttons_layout.addWidget(self.btn_apply)
        
        layout.addLayout(buttons_layout)
        
    def populate_layout_list(self):
        """Populate the layout list"""
        self.layout_list.clear()
        
        # Add presets
        item = QListWidgetItem("═══ Dispositions Prédéfinies ═══")
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.layout_list.addItem(item)
        
        for name, data in self.layout_manager.PRESETS.items():
            item = QListWidgetItem(f"🎨 {data['name']}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            item.setData(Qt.ItemDataRole.UserRole + 1, 'preset')
            self.layout_list.addItem(item)
        
        # Add custom layouts
        if self.layout_manager.get_custom_names():
            item = QListWidgetItem("\n═══ Dispositions Personnalisées ═══")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.layout_list.addItem(item)
            
            for name in self.layout_manager.get_custom_names():
                item = QListWidgetItem(f"⭐ {name}")
                item.setData(Qt.ItemDataRole.UserRole, name)
                item.setData(Qt.ItemDataRole.UserRole + 1, 'custom')
                self.layout_list.addItem(item)
        
    def on_layout_selected(self, item: QListWidgetItem):
        """Handle layout selection"""
        layout_name = item.data(Qt.ItemDataRole.UserRole)
        layout_type = item.data(Qt.ItemDataRole.UserRole + 1)
        
        if not layout_name:
            return
        
        if layout_type == 'preset':
            self.current_layout = self.layout_manager.get_preset(layout_name)
        else:
            self.current_layout = self.layout_manager.custom_layouts.get(layout_name)
        
        if self.current_layout:
            self.update_ui_from_layout()
            self.update_description()
    
    def update_ui_from_layout(self):
        """Update UI controls from current layout"""
        # Update checkboxes
        for key, check in self.panel_checks.items():
            check.setChecked(self.current_layout.panels_visible.get(key, True))
        
        # Update splitter slider
        left_percent = int((self.current_layout.splitter_sizes[0] / sum(self.current_layout.splitter_sizes)) * 100)
        self.splitter_slider.setValue(left_percent)
        self.splitter_label.setText(f"{left_percent}% / {100-left_percent}%")
    
    def update_description(self):
        """Update description text"""
        if not self.current_layout:
            return
        
        desc = f"<h3>{self.current_layout.name}</h3>"
        desc += "<ul>"
        desc += f"<li><b>Panels visibles:</b> {sum(self.current_layout.panels_visible.values())}/6</li>"
        desc += f"<li><b>Ratio échiquier/panneau:</b> {self.splitter_label.text()}</li>"
        desc += "</ul>"
        
        self.desc_text.setHtml(desc)
    
    def on_panel_visibility_changed(self, key: str, state):
        """Handle panel visibility change"""
        self.current_layout.panels_visible[key] = (state == Qt.CheckState.Checked.value)
        self.update_description()
    
    def on_splitter_changed(self, value):
        """Handle splitter slider change"""
        left = value
        right = 100 - value
        
        # Update sizes (assuming total width of 1600)
        total = 1600
        self.current_layout.splitter_sizes = [int(total * left / 100), int(total * right / 100)]
        
        self.splitter_label.setText(f"{left}% / {right}%")
        self.update_description()
    
    def create_new_layout(self):
        """Create a new custom layout"""
        name, ok = QInputDialog.getText(
            self,
            "Nouvelle Disposition",
            "Nom de la disposition:"
        )
        
        if ok and name:
            # Create new layout based on current
            new_layout = LayoutConfig(name)
            new_layout.splitter_sizes = self.current_layout.splitter_sizes.copy()
            new_layout.panels_visible = self.current_layout.panels_visible.copy()
            
            # Save it
            self.layout_manager.save_layout(new_layout, as_custom=True)
            
            # Refresh list
            self.populate_layout_list()
            
            QMessageBox.information(self, "Succès", f"Disposition '{name}' créée !")
    
    def delete_layout(self):
        """Delete selected custom layout"""
        current_item = self.layout_list.currentItem()
        if not current_item:
            return
        
        layout_type = current_item.data(Qt.ItemDataRole.UserRole + 1)
        if layout_type != 'custom':
            QMessageBox.warning(self, "Erreur", "Vous ne pouvez supprimer que les dispositions personnalisées")
            return
        
        layout_name = current_item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Supprimer la disposition '{layout_name}' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.layout_manager.delete_layout(layout_name)
            self.populate_layout_list()
            QMessageBox.information(self, "Succès", "Disposition supprimée")
    
    def export_layout(self):
        """Export current layout to file"""
        if not self.current_layout:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter la Disposition",
            f"{self.current_layout.name}.json",
            "Fichiers JSON (*.json)"
        )
        
        if file_path:
            from pathlib import Path
            self.layout_manager.export_layout(self.current_layout, Path(file_path))
            QMessageBox.information(self, "Succès", "Disposition exportée !")
    
    def import_layout(self):
        """Import layout from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importer une Disposition",
            "",
            "Fichiers JSON (*.json)"
        )
        
        if file_path:
            from pathlib import Path
            layout = self.layout_manager.import_layout(Path(file_path))
            if layout:
                # Save as custom
                self.layout_manager.save_layout(layout, as_custom=True)
                self.populate_layout_list()
                QMessageBox.information(self, "Succès", f"Disposition '{layout.name}' importée !")
            else:
                QMessageBox.warning(self, "Erreur", "Impossible d'importer la disposition")
    
    def preview_layout(self):
        """Preview the layout"""
        self.layout_changed.emit(self.current_layout)
        self.statusBar().showMessage("Aperçu appliqué", 2000)
    
    def apply_layout(self):
        """Apply and save the layout"""
        self.layout_manager.apply_layout(self.current_layout)
        self.layout_changed.emit(self.current_layout)
        self.accept()
    
    def get_selected_layout(self) -> LayoutConfig:
        """Get the selected layout"""
        return self.current_layout

