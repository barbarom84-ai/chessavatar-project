"""
Avatar Creation Dialog - Interface for creating AI avatars
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QTextEdit,
                             QProgressBar, QFileDialog, QMessageBox, QGroupBox,
                             QFormLayout, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
from pathlib import Path
from typing import Optional

from core.api_service import APIService
from core.style_analyzer import StyleAnalyzer, PlayerStyle
from core.avatar_manager import AvatarManager


class FetchGamesWorker(QThread):
    """Worker thread for fetching games"""
    
    progress = pyqtSignal(int, str)  # (percentage, message)
    finished = pyqtSignal(object, object)  # (games, player_style)
    error = pyqtSignal(str)
    
    def __init__(self, platform: str, username: str):
        super().__init__()
        self.platform = platform
        self.username = username
        self.api_service = APIService()
        self.style_analyzer = StyleAnalyzer()
        
    def run(self):
        """Fetch and analyze games"""
        try:
            # Verify username
            self.progress.emit(10, f"Vérification de {self.username}...")
            if not self.api_service.verify_username(self.platform, self.username):
                self.error.emit(f"Utilisateur '{self.username}' non trouvé sur {self.platform}")
                return
                
            # Fetch games
            self.progress.emit(30, "Récupération des parties...")
            
            if self.platform == 'lichess':
                games = self.api_service.fetch_lichess_games(self.username, max_games=100)
            else:  # chesscom
                games = self.api_service.fetch_chesscom_games(self.username, max_games=100)
                
            if not games:
                self.error.emit("Aucune partie trouvée pour cet utilisateur")
                return
                
            self.progress.emit(70, f"{len(games)} parties récupérées. Analyse en cours...")
            
            # Analyze style
            player_style = self.style_analyzer.analyze_games(
                games, 
                self.username,
                "Lichess" if self.platform == 'lichess' else "Chess.com"
            )
            
            self.progress.emit(100, "Analyse terminée!")
            self.finished.emit(games, player_style)
            
        except Exception as e:
            self.error.emit(f"Erreur: {str(e)}")


class AvatarCreationDialog(QDialog):
    """Dialog for creating AI avatars from real players"""
    
    avatar_created = pyqtSignal(str)  # avatar_id
    
    def __init__(self, avatar_manager: AvatarManager, parent=None):
        super().__init__(parent)
        self.avatar_manager = avatar_manager
        self.player_style: Optional[PlayerStyle] = None
        self.photo_path: Optional[str] = None
        self.worker: Optional[FetchGamesWorker] = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Créer un Avatar IA")
        self.setMinimumSize(700, 800)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🤖 Créer un Avatar IA Personnalisé")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #d4d4d4;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "Récupérez le profil d'un joueur depuis Lichess ou Chess.com\n"
            "et créez une IA qui imite son style de jeu!"
        )
        instructions.setStyleSheet("color: #888888; font-size: 10pt;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)
        
        # Input section
        input_group = QGroupBox("Informations du Joueur")
        input_layout = QFormLayout(input_group)
        
        # Platform selection
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Lichess", "Chess.com"])
        self.platform_combo.setStyleSheet("""
            QComboBox {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 6px;
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
        input_layout.addRow("Plateforme:", self.platform_combo)
        
        # Username input
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Nom d'utilisateur...")
        self.username_edit.setStyleSheet("""
            QLineEdit {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 6px;
            }
            QLineEdit:focus {
                border: 1px solid #0e639c;
            }
        """)
        input_layout.addRow("Utilisateur:", self.username_edit)
        
        # Display name
        self.display_name_edit = QLineEdit()
        self.display_name_edit.setPlaceholderText("Nom d'affichage (optionnel)...")
        self.display_name_edit.setStyleSheet(self.username_edit.styleSheet())
        input_layout.addRow("Nom d'affichage:", self.display_name_edit)
        
        layout.addWidget(input_group)
        
        # Photo section
        photo_group = QGroupBox("Photo de Profil")
        photo_layout = QHBoxLayout(photo_group)
        
        self.photo_label = QLabel("Aucune photo")
        self.photo_label.setFixedSize(100, 100)
        self.photo_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 2px solid #3e3e3e;
                border-radius: 8px;
                color: #888888;
            }
        """)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setScaledContents(True)
        photo_layout.addWidget(self.photo_label)
        
        photo_buttons_layout = QVBoxLayout()
        
        self.upload_photo_button = QPushButton("📁 Choisir une photo")
        self.upload_photo_button.clicked.connect(self.upload_photo)
        photo_buttons_layout.addWidget(self.upload_photo_button)
        
        self.clear_photo_button = QPushButton("✖ Supprimer")
        self.clear_photo_button.clicked.connect(self.clear_photo)
        self.clear_photo_button.setEnabled(False)
        photo_buttons_layout.addWidget(self.clear_photo_button)
        
        photo_buttons_layout.addStretch()
        photo_layout.addLayout(photo_buttons_layout)
        photo_layout.addStretch()
        
        layout.addWidget(photo_group)
        
        # Fetch button
        self.fetch_button = QPushButton("🔍 Récupérer et Analyser")
        self.fetch_button.setMinimumHeight(40)
        self.fetch_button.clicked.connect(self.fetch_games)
        layout.addWidget(self.fetch_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #252526;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                text-align: center;
                color: #d4d4d4;
            }
            QProgressBar::chunk {
                background-color: #0e639c;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888888; font-style: italic;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Style report
        self.style_report = QTextEdit()
        self.style_report.setReadOnly(True)
        self.style_report.setPlaceholderText("Le profil du joueur apparaîtra ici après l'analyse...")
        self.style_report.setMinimumHeight(200)
        self.style_report.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
            }
        """)
        layout.addWidget(self.style_report)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.create_button = QPushButton("✔ Créer l'Avatar")
        self.create_button.setEnabled(False)
        self.create_button.setMinimumWidth(150)
        self.create_button.clicked.connect(self.create_avatar)
        button_layout.addWidget(self.create_button)
        
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def upload_photo(self):
        """Upload avatar photo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une photo",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.photo_path = file_path
            pixmap = QPixmap(file_path)
            self.photo_label.setPixmap(pixmap)
            self.clear_photo_button.setEnabled(True)
            
    def clear_photo(self):
        """Clear selected photo"""
        self.photo_path = None
        self.photo_label.setPixmap(QPixmap())
        self.photo_label.setText("Aucune photo")
        self.clear_photo_button.setEnabled(False)
        
    def fetch_games(self):
        """Fetch and analyze games"""
        username = self.username_edit.text().strip()
        if not username:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un nom d'utilisateur")
            return
            
        platform = 'lichess' if self.platform_combo.currentText() == "Lichess" else 'chesscom'
        
        # Disable inputs
        self.fetch_button.setEnabled(False)
        self.username_edit.setEnabled(False)
        self.platform_combo.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start worker thread
        self.worker = FetchGamesWorker(platform, username)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_fetch_finished)
        self.worker.error.connect(self.on_fetch_error)
        self.worker.start()
        
    def on_progress(self, percentage: int, message: str):
        """Handle progress update"""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)
        
    def on_fetch_finished(self, games, player_style: PlayerStyle):
        """Handle fetch completion"""
        self.player_style = player_style
        
        # Display style report
        from core.style_analyzer import StyleAnalyzer
        analyzer = StyleAnalyzer()
        report = analyzer.generate_style_report(player_style)
        self.style_report.setPlainText(report)
        
        # Enable create button
        self.create_button.setEnabled(True)
        
        # Reset UI
        self.fetch_button.setEnabled(True)
        self.username_edit.setEnabled(True)
        self.platform_combo.setEnabled(True)
        
        QMessageBox.information(
            self,
            "Analyse terminée",
            f"Profil analysé avec succès!\n\n"
            f"{len(games)} parties analysées\n"
            f"Elo moyen: {player_style.average_elo}\n"
            f"Niveau estimé: {player_style.estimated_skill_level}/20"
        )
        
    def on_fetch_error(self, error_message: str):
        """Handle fetch error"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("")
        
        self.fetch_button.setEnabled(True)
        self.username_edit.setEnabled(True)
        self.platform_combo.setEnabled(True)
        
        QMessageBox.critical(self, "Erreur", error_message)
        
    def create_avatar(self):
        """Create the avatar"""
        if not self.player_style:
            return
            
        username = self.username_edit.text().strip()
        platform = 'lichess' if self.platform_combo.currentText() == "Lichess" else 'chesscom'
        display_name = self.display_name_edit.text().strip() or username
        
        try:
            avatar = self.avatar_manager.create_avatar(
                username=username,
                platform=platform,
                player_style=self.player_style,
                display_name=display_name,
                photo_path=self.photo_path
            )
            
            self.avatar_created.emit(avatar.id)
            
            QMessageBox.information(
                self,
                "Succès",
                f"Avatar '{display_name}' créé avec succès!\n\n"
                f"Vous pouvez maintenant jouer contre cette IA."
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {str(e)}")

