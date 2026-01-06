"""
Engine configuration dialog for managing chess engines
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QLabel, QLineEdit, QFileDialog,
                             QMessageBox, QComboBox, QGroupBox, QFormLayout,
                             QListWidgetItem, QSpinBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
import json
import os
from typing import List
from core.engine_manager import EngineInfo


class EngineConfigDialog(QDialog):
    """Dialog for configuring chess engines"""
    
    # Signal emitted when engines list changes
    engines_changed = pyqtSignal()
    
    def __init__(self, engines: List[EngineInfo], parent=None):
        super().__init__(parent)
        self.engines = engines.copy()
        self.config_file = Path("engines_config.json")
        self.init_ui()
        self.load_engines_to_list()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Configuration des Moteurs")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Gestion des Moteurs d'Échecs")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #d4d4d4;")
        layout.addWidget(title)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left side - Engine list
        left_layout = QVBoxLayout()
        
        list_label = QLabel("Moteurs configurés:")
        list_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(list_label)
        
        self.engine_list = QListWidget()
        self.engine_list.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 5px;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #0e639c;
            }
            QListWidget::item:hover {
                background-color: #3e3e3e;
            }
        """)
        self.engine_list.itemSelectionChanged.connect(self.on_selection_changed)
        left_layout.addWidget(self.engine_list)
        
        # Buttons for list management
        list_buttons = QHBoxLayout()
        
        self.add_button = QPushButton("➕ Ajouter")
        self.add_button.clicked.connect(self.add_engine)
        list_buttons.addWidget(self.add_button)
        
        self.remove_button = QPushButton("➖ Supprimer")
        self.remove_button.setEnabled(False)
        self.remove_button.clicked.connect(self.remove_engine)
        list_buttons.addWidget(self.remove_button)
        
        left_layout.addLayout(list_buttons)
        content_layout.addLayout(left_layout, stretch=1)
        
        # Right side - Engine details
        right_layout = QVBoxLayout()
        
        details_group = QGroupBox("Détails du Moteur")
        details_group.setStyleSheet("""
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
        """)
        details_layout = QFormLayout(details_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nom du moteur...")
        self.name_edit.setStyleSheet("""
            QLineEdit {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 6px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 1px solid #0e639c;
            }
        """)
        details_layout.addRow("Nom:", self.name_edit)
        
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Chemin vers l'exécutable...")
        self.path_edit.setStyleSheet(self.name_edit.styleSheet())
        self.path_edit.setReadOnly(True)
        path_layout.addWidget(self.path_edit)
        
        self.browse_button = QPushButton("📁 Parcourir")
        self.browse_button.setMaximumWidth(120)
        self.browse_button.clicked.connect(self.browse_engine)
        path_layout.addWidget(self.browse_button)
        details_layout.addRow("Chemin:", path_layout)
        
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["UCI", "WinBoard"])
        self.protocol_combo.setStyleSheet("""
            QComboBox {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 6px;
                font-size: 10pt;
            }
            QComboBox:focus {
                border: 1px solid #0e639c;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #252526;
                color: #d4d4d4;
                selection-background-color: #0e639c;
            }
        """)
        details_layout.addRow("Protocole:", self.protocol_combo)
        
        right_layout.addWidget(details_group)
        
        # UCI Options Group
        uci_group = QGroupBox("Options UCI")
        uci_group.setStyleSheet(details_group.styleSheet())
        uci_layout = QFormLayout(uci_group)
        
        # Get CPU count for max threads
        cpu_count = os.cpu_count() or 1
        
        # Threads spinbox
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, cpu_count)
        self.threads_spin.setValue(cpu_count)
        self.threads_spin.setMinimumHeight(35)
        self.threads_spin.setMinimumWidth(150)
        self.threads_spin.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)
        self.threads_spin.setStyleSheet("""
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
            QSpinBox::up-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 6px solid #d4d4d4;
            }
            QSpinBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #d4d4d4;
            }
        """)
        self.threads_spin.setSuffix(f" / {cpu_count}")
        self.threads_spin.setToolTip(f"Nombre de threads CPU à utiliser (1 à {cpu_count})")
        uci_layout.addRow("Threads:", self.threads_spin)
        
        # Hash spinbox
        self.hash_spin = QSpinBox()
        self.hash_spin.setRange(16, 4096)
        self.hash_spin.setValue(256)
        self.hash_spin.setSingleStep(64)
        self.hash_spin.setMinimumHeight(35)
        self.hash_spin.setMinimumWidth(150)
        self.hash_spin.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)
        self.hash_spin.setStyleSheet(self.threads_spin.styleSheet())
        self.hash_spin.setSuffix(" MB")
        self.hash_spin.setToolTip("Mémoire allouée à la table de hachage (16 à 4096 MB)")
        uci_layout.addRow("Hash:", self.hash_spin)
        
        # MultiPV spinbox
        self.multipv_spin = QSpinBox()
        self.multipv_spin.setRange(1, 5)
        self.multipv_spin.setValue(3)
        self.multipv_spin.setMinimumHeight(35)
        self.multipv_spin.setMinimumWidth(150)
        self.multipv_spin.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)
        self.multipv_spin.setStyleSheet(self.threads_spin.styleSheet())
        self.multipv_spin.setToolTip("Nombre de meilleures lignes à afficher (1 à 5)")
        uci_layout.addRow("MultiPV:", self.multipv_spin)
        
        # Ponder checkbox
        self.ponder_check = QCheckBox()
        self.ponder_check.setChecked(False)
        self.ponder_check.setMinimumHeight(35)
        self.ponder_check.setStyleSheet("""
            QCheckBox {
                color: #d4d4d4;
                font-size: 11pt;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
                border: 2px solid #3e3e3e;
                border-radius: 4px;
                background-color: #252526;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #0e639c;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #0e639c;
                border: 2px solid #1177bb;
            }
        """)
        self.ponder_check.setToolTip("Réflexion pendant le tour de l'adversaire")
        uci_layout.addRow("Ponder:", self.ponder_check)
        
        # Skill Level spinbox
        self.skill_level_spin = QSpinBox()
        self.skill_level_spin.setRange(-1, 20)
        self.skill_level_spin.setValue(-1)
        self.skill_level_spin.setMinimumHeight(35)
        self.skill_level_spin.setMinimumWidth(150)
        self.skill_level_spin.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)
        self.skill_level_spin.setStyleSheet(self.threads_spin.styleSheet())
        self.skill_level_spin.setSpecialValueText("Max (désactivé)")
        self.skill_level_spin.setToolTip("Niveau de jeu : -1 = Force max, 0 = Débutant, 20 = Expert")
        uci_layout.addRow("Skill Level:", self.skill_level_spin)
        
        right_layout.addWidget(uci_group)
        
        # Save button
        self.save_button = QPushButton("💾 Sauvegarder")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_engine)
        right_layout.addWidget(self.save_button)
        
        # Info label
        info_label = QLabel(
            "ℹ️ Moteurs UCI supportés:\n"
            "• Stockfish\n"
            "• Komodo\n"
            "• Leela Chess Zero\n"
            "• Et d'autres moteurs UCI compatibles"
        )
        info_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 10px;
                color: #888888;
                font-size: 9pt;
            }
        """)
        right_layout.addWidget(info_label)
        
        right_layout.addStretch()
        content_layout.addLayout(right_layout, stretch=1)
        
        layout.addLayout(content_layout)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_button = QPushButton("Fermer")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Load saved engines
        self.load_engines_from_config()
        
    def load_engines_to_list(self):
        """Load engines to the list widget"""
        self.engine_list.clear()
        for engine in self.engines:
            item = QListWidgetItem(f"🔧 {engine.name}")
            item.setData(Qt.ItemDataRole.UserRole, engine)
            self.engine_list.addItem(item)
            
    def on_selection_changed(self):
        """Handle selection change in engine list"""
        items = self.engine_list.selectedItems()
        if items:
            self.remove_button.setEnabled(True)
            self.save_button.setEnabled(True)  # Enable save button when engine is selected
            engine: EngineInfo = items[0].data(Qt.ItemDataRole.UserRole)
            self.name_edit.setText(engine.name)
            self.path_edit.setText(engine.path)
            self.protocol_combo.setCurrentText(engine.protocol)
            
            # Load UCI options
            cpu_count = os.cpu_count() or 1
            self.threads_spin.setValue(engine.options.get("Threads", cpu_count))
            self.hash_spin.setValue(engine.options.get("Hash", 256))
            self.multipv_spin.setValue(engine.options.get("MultiPV", 3))
            self.ponder_check.setChecked(engine.options.get("Ponder", False))
            self.skill_level_spin.setValue(engine.options.get("Skill Level", -1))
        else:
            self.remove_button.setEnabled(False)
            self.save_button.setEnabled(False)  # Disable save button when nothing is selected
            
    def add_engine(self):
        """Add new engine"""
        self.engine_list.clearSelection()
        self.name_edit.clear()
        self.path_edit.clear()
        self.protocol_combo.setCurrentIndex(0)
        
        # Reset UCI options to defaults
        cpu_count = os.cpu_count() or 1
        self.threads_spin.setValue(cpu_count)
        self.hash_spin.setValue(256)
        self.multipv_spin.setValue(3)
        self.ponder_check.setChecked(False)
        self.skill_level_spin.setValue(-1)
        
        self.save_button.setEnabled(True)
        self.name_edit.setFocus()
        
    def remove_engine(self):
        """Remove selected engine"""
        items = self.engine_list.selectedItems()
        if not items:
            return
            
        reply = QMessageBox.question(
            self,
            "Supprimer le moteur",
            "Voulez-vous vraiment supprimer ce moteur ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            engine: EngineInfo = items[0].data(Qt.ItemDataRole.UserRole)
            self.engines = [e for e in self.engines if e.name != engine.name]
            self.load_engines_to_list()
            self.save_engines_to_config()
            self.engines_changed.emit()
            
            # Clear form
            self.name_edit.clear()
            self.path_edit.clear()
            self.remove_button.setEnabled(False)
            
    def browse_engine(self):
        """Browse for engine executable"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un moteur d'échecs",
            "",
            "Exécutables (*.exe);;Tous les fichiers (*.*)"
        )
        
        if file_path:
            self.path_edit.setText(file_path)
            # Auto-fill name if empty
            if not self.name_edit.text():
                engine_name = Path(file_path).stem
                self.name_edit.setText(engine_name)
            self.save_button.setEnabled(True)
            
    def save_engine(self):
        """Save engine configuration"""
        name = self.name_edit.text().strip()
        path = self.path_edit.text().strip()
        protocol = self.protocol_combo.currentText()
        
        # Validate
        if not name:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un nom pour le moteur")
            return
            
        if not path:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un fichier exécutable")
            return
            
        if not Path(path).exists():
            QMessageBox.warning(self, "Erreur", "Le fichier spécifié n'existe pas")
            return
        
        # Get UCI options
        uci_options = {
            "Threads": self.threads_spin.value(),
            "Hash": self.hash_spin.value(),
            "MultiPV": self.multipv_spin.value(),
            "Ponder": self.ponder_check.isChecked(),
            "Skill Level": self.skill_level_spin.value()
        }
            
        # Check if name already exists (for new engines)
        existing = next((e for e in self.engines if e.name == name), None)
        if existing:
            # Update existing
            existing.path = path
            existing.protocol = protocol
            existing.options = uci_options
        else:
            # Add new
            new_engine = EngineInfo(name, path, protocol)
            new_engine.options = uci_options
            self.engines.append(new_engine)
            
        self.load_engines_to_list()
        self.save_engines_to_config()
        self.engines_changed.emit()
        self.save_button.setEnabled(False)
        
        QMessageBox.information(
            self, 
            "Succès", 
            f"Moteur '{name}' et ses options UCI sauvegardés avec succès !\n\n"
            f"Redémarrez le moteur pour appliquer les changements."
        )
        
    def load_engines_from_config(self):
        """Load engines from config file"""
        if not self.config_file.exists():
            return
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.engines = [EngineInfo.from_dict(e) for e in data.get('engines', [])]
                self.load_engines_to_list()
        except Exception as e:
            print(f"Failed to load engines config: {e}")
            
    def save_engines_to_config(self):
        """Save engines to config file"""
        try:
            data = {
                'engines': [e.to_dict() for e in self.engines]
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save engines config: {e}")
            
    def get_engines(self) -> List[EngineInfo]:
        """Get the current list of engines"""
        return self.engines.copy()

