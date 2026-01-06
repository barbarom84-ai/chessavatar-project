"""
Avatar Panel - Display and manage AI avatars
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem, QGroupBox,
                             QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
from pathlib import Path
from typing import Optional

from core.avatar_manager import AvatarManager, Avatar


class AvatarListItem(QWidget):
    """Custom widget for avatar list item"""
    
    play_clicked = pyqtSignal(str)  # avatar_id
    configure_clicked = pyqtSignal(str)  # avatar_id
    delete_clicked = pyqtSignal(str)  # avatar_id
    
    def __init__(self, avatar: Avatar, parent=None):
        super().__init__(parent)
        self.avatar = avatar
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Avatar photo
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(50, 50)
        self.photo_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
            }
        """)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setScaledContents(True)
        
        if self.avatar.photo_path and Path(self.avatar.photo_path).exists():
            pixmap = QPixmap(self.avatar.photo_path)
            self.photo_label.setPixmap(pixmap)
        else:
            self.photo_label.setText("👤")
            self.photo_label.setStyleSheet(self.photo_label.styleSheet() + "font-size: 24pt;")
            
        layout.addWidget(self.photo_label)
        
        # Avatar info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        name_label = QLabel(self.avatar.display_name)
        name_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #d4d4d4;")
        info_layout.addWidget(name_label)
        
        # Style info with stars rating
        style_data = self.avatar.style_data
        elo = style_data.get('average_elo', 1500)
        win_rate = style_data.get('win_rate', 0) * 100  # Convert to percentage
        skill = style_data.get('estimated_skill_level', 10)
        
        # Star rating based on skill level (0-20 → 1-5 stars)
        star_count = min(5, max(1, (skill + 2) // 4))  # 0-3→1★, 4-7→2★, 8-11→3★, 12-15→4★, 16-20→5★
        stars = "★" * star_count + "☆" * (5 - star_count)
        
        stats_label = QLabel(f"{self.avatar.platform.title()} | Elo: {elo} | {stars}")
        stats_label.setStyleSheet("font-size: 9pt; color: #888888;")
        info_layout.addWidget(stats_label)
        
        # Win rate and style
        play_style = style_data.get('play_style', 'Équilibré')
        games_label = QLabel(f"Victoires: {win_rate:.0f}% | Style: {play_style}")
        games_label.setStyleSheet("font-size: 9pt; color: #888888;")
        info_layout.addWidget(games_label)
        
        layout.addLayout(info_layout, stretch=1)
        
        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)
        
        play_button = QPushButton("▶ Jouer")
        play_button.setMaximumWidth(90)
        play_button.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        play_button.clicked.connect(lambda: self.play_clicked.emit(self.avatar.id))
        button_layout.addWidget(play_button)
        
        config_button = QPushButton("⚙ Config")
        config_button.setMaximumWidth(90)
        config_button.setStyleSheet("""
            QPushButton {
                background-color: #424242;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        config_button.clicked.connect(lambda: self.configure_clicked.emit(self.avatar.id))
        button_layout.addWidget(config_button)
        
        delete_button = QPushButton("🗑")
        delete_button.setMaximumWidth(90)
        delete_button.setToolTip("Supprimer cet avatar")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
            }
            QPushButton:hover {
                background-color: #f44336;
            }
        """)
        delete_button.clicked.connect(lambda: self.delete_clicked.emit(self.avatar.id))
        button_layout.addWidget(delete_button)
        
        layout.addLayout(button_layout)


class AvatarPanel(QWidget):
    """Panel for managing and selecting AI avatars"""
    
    avatar_selected = pyqtSignal(str)  # avatar_id
    avatar_configure_requested = pyqtSignal(str)  # avatar_id
    create_avatar_requested = pyqtSignal()
    
    def __init__(self, avatar_manager: AvatarManager, parent=None):
        super().__init__(parent)
        self.avatar_manager = avatar_manager
        self.init_ui()
        self.load_avatars()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🤖 Avatars IA")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #d4d4d4;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Create button
        self.create_button = QPushButton("➕ Créer un Avatar")
        self.create_button.clicked.connect(self.on_create_avatar)
        header_layout.addWidget(self.create_button)
        
        layout.addLayout(header_layout)
        
        # Description
        desc = QLabel(
            "Créez des IA qui imitent le style de vrais joueurs.\n"
            "Analysez leurs parties et jouez contre leur réplique!"
        )
        desc.setStyleSheet("color: #888888; font-size: 9pt;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Avatars list
        list_label = QLabel("Mes Avatars:")
        list_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        layout.addWidget(list_label)
        
        self.avatar_list = QListWidget()
        self.avatar_list.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
            }
            QListWidget::item {
                border-bottom: 1px solid #3e3e3e;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #0e639c;
            }
            QListWidget::item:hover {
                background-color: #3e3e3e;
            }
        """)
        self.avatar_list.setSpacing(2)
        layout.addWidget(self.avatar_list)
        
        # Statistics
        stats_group = QGroupBox("Statistiques")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("Aucun avatar créé")
        self.stats_label.setStyleSheet("color: #888888; font-size: 9pt;")
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(stats_group)
        
        layout.addStretch()
        
    def load_avatars(self):
        """Load avatars into list"""
        self.avatar_list.clear()
        avatars = self.avatar_manager.get_all_avatars()
        
        if not avatars:
            # Show empty state
            item = QListWidgetItem(self.avatar_list)
            empty_widget = QLabel("Aucun avatar. Créez-en un!")
            empty_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_widget.setStyleSheet("color: #888888; padding: 20px;")
            item.setSizeHint(empty_widget.sizeHint())
            self.avatar_list.addItem(item)
            self.avatar_list.setItemWidget(item, empty_widget)
        else:
            for avatar in avatars:
                item = QListWidgetItem(self.avatar_list)
                avatar_widget = AvatarListItem(avatar)
                avatar_widget.play_clicked.connect(self.on_play_avatar)
                avatar_widget.configure_clicked.connect(self.on_configure_avatar)
                avatar_widget.delete_clicked.connect(self.on_delete_avatar)
                
                item.setSizeHint(avatar_widget.sizeHint())
                self.avatar_list.addItem(item)
                self.avatar_list.setItemWidget(item, avatar_widget)
                
        self.update_statistics()
        
    def update_statistics(self):
        """Update statistics display"""
        stats = self.avatar_manager.get_statistics()
        
        text = f"Total: {stats['total_avatars']} avatar(s)\n"
        text += f"Parties jouées: {stats['total_games']}\n"
        
        if stats['platforms']:
            text += "\nPar plateforme:\n"
            for platform, count in stats['platforms'].items():
                text += f"  • {platform}: {count}\n"
                
        self.stats_label.setText(text)
        
    def on_create_avatar(self):
        """Handle create avatar button"""
        self.create_avatar_requested.emit()
        
    def on_play_avatar(self, avatar_id: str):
        """Handle play button"""
        self.avatar_selected.emit(avatar_id)
    
    def on_configure_avatar(self, avatar_id: str):
        """Handle configure button"""
        self.avatar_configure_requested.emit(avatar_id)
        
    def on_delete_avatar(self, avatar_id: str):
        """Handle delete button"""
        avatar = self.avatar_manager.get_avatar(avatar_id)
        if not avatar:
            return
            
        reply = QMessageBox.question(
            self,
            "Supprimer l'avatar",
            f"Voulez-vous vraiment supprimer l'avatar '{avatar.display_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.avatar_manager.delete_avatar(avatar_id):
                self.load_avatars()
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Avatar '{avatar.display_name}' supprimé"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    "Impossible de supprimer l'avatar"
                )
                
    def refresh(self):
        """Refresh avatar list"""
        self.load_avatars()


class AvatarStatusWidget(QWidget):
    """Widget showing currently active avatar"""
    
    # Signal emitted when user wants to change/select avatar
    change_avatar_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_avatar: Optional[Avatar] = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Photo
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(80, 80)
        self.photo_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 2px solid #3e3e3e;
                border-radius: 8px;
            }
        """)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setScaledContents(True)
        layout.addWidget(self.photo_label)
        
        # Info
        info_layout = QVBoxLayout()
        
        self.name_label = QLabel("Aucun adversaire")
        self.name_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #d4d4d4;")
        info_layout.addWidget(self.name_label)
        
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("font-size: 10pt; color: #888888;")
        info_layout.addWidget(self.stats_label)
        
        self.style_label = QLabel("")
        self.style_label.setStyleSheet("font-size: 9pt; color: #888888;")
        info_layout.addWidget(self.style_label)
        
        layout.addLayout(info_layout, stretch=1)
        
        # Button to change/select avatar
        self.change_button = QPushButton("Changer")
        self.change_button.setFixedWidth(100)
        self.change_button.clicked.connect(self.change_avatar_clicked.emit)
        layout.addWidget(self.change_button)
        
        self.clear()
        
    def set_avatar(self, avatar: Avatar):
        """Set active avatar"""
        self.current_avatar = avatar
        
        # Photo
        if avatar.photo_path and Path(avatar.photo_path).exists():
            pixmap = QPixmap(avatar.photo_path)
            self.photo_label.setPixmap(pixmap)
        else:
            self.photo_label.setText("👤")
            self.photo_label.setStyleSheet(self.photo_label.styleSheet() + "font-size: 48pt;")
            
        # Name
        self.name_label.setText(f"Adversaire: {avatar.display_name}")
        
        # Stats
        style = avatar.style_data
        self.stats_label.setText(
            f"{avatar.platform} | Elo {style.get('average_elo', 1500)} | "
            f"Niveau {style.get('estimated_skill_level', 10)}/20"
        )
        
        # Style
        aggressive = style.get('aggressive_score', 50)
        tactical = style.get('tactical_score', 50)
        
        style_desc = "Style: "
        if aggressive > 65:
            style_desc += "Agressif"
        elif aggressive < 35:
            style_desc += "Positionnel"
        else:
            style_desc += "Équilibré"
            
        if tactical > 65:
            style_desc += " • Tactique"
        else:
            style_desc += " • Stratégique"
            
        self.style_label.setText(style_desc)
        
    def clear(self):
        """Clear avatar display"""
        self.current_avatar = None
        self.photo_label.clear()
        self.photo_label.setText("❓")
        self.photo_label.setStyleSheet(
            self.photo_label.styleSheet().split("font-size")[0] + "font-size: 48pt;"
        )
        self.name_label.setText("Aucun adversaire")
        self.stats_label.setText("Sélectionnez un avatar pour jouer")
        self.style_label.setText("")

