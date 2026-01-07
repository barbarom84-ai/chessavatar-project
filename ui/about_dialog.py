"""
About dialog showing application information
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTextBrowser)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
import sys


class AboutDialog(QDialog):
    """About dialog with app information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("À propos de ChessAvatar")
        self.setFixedSize(600, 500)
        
        layout = QVBoxLayout()
        
        # Logo/Title section
        title_layout = QHBoxLayout()
        
        # Icon (if exists)
        icon_label = QLabel("♟️")
        icon_label.setFont(QFont("Segoe UI", 48))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(icon_label)
        
        # Title
        title = QLabel("ChessAvatar")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title)
        
        layout.addLayout(title_layout)
        
        # Version
        version = QLabel("Version 1.0.0")
        version.setFont(QFont("Segoe UI", 12))
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        # Description
        desc = QTextBrowser()
        desc.setOpenExternalLinks(True)
        desc.setHtml("""
        <div style='text-align: center; padding: 20px;'>
            <h3>🎮 Échecs avec Intelligence Artificielle Personnalisée</h3>
            
            <p style='margin-top: 20px; line-height: 1.6;'>
                <b>ChessAvatar</b> est une application d'échecs innovante qui utilise l'IA pour 
                créer des adversaires virtuels basés sur le style de jeu de vrais joueurs.
            </p>
            
            <h4 style='margin-top: 20px;'>✨ Fonctionnalités principales</h4>
            <ul style='text-align: left; line-height: 1.8;'>
                <li>🤖 <b>Avatars IA personnalisés</b> - Clonez le style de n'importe quel joueur</li>
                <li>♟️ <b>Multiples modes de jeu</b> - Humain, Moteur, Avatar (tous vs tous)</li>
                <li>🎨 <b>16 thèmes visuels</b> - Personnalisez l'apparence de l'échiquier</li>
                <li>📊 <b>Analyse de parties</b> - Moteur Stockfish intégré</li>
                <li>📖 <b>Bibliothèque d'ouvertures</b> - Reconnaissance ECO automatique</li>
                <li>💾 <b>Import/Export PGN</b> - Compatible avec tous les standards</li>
                <li>🎯 <b>Entraînement adaptatif</b> - L'IA s'adapte à votre niveau</li>
            </ul>
            
            <h4 style='margin-top: 20px;'>🛠️ Technologies</h4>
            <p style='line-height: 1.6;'>
                • Python {python_version}<br>
                • PyQt6 - Interface graphique<br>
                • python-chess - Logique du jeu<br>
                • Stockfish - Moteur d'échecs<br>
                • Matplotlib - Visualisations
            </p>
            
            <h4 style='margin-top: 20px;'>👨‍💻 Développement</h4>
            <p>
                Développé avec ❤️ par la communauté open-source<br>
                <a href='https://github.com/yourusername/chessavatar'>GitHub</a> | 
                <a href='https://chessavatar.app'>Website</a>
            </p>
            
            <p style='margin-top: 20px; font-size: 10pt; color: #888;'>
                © 2025 ChessAvatar Project. Distribué sous licence MIT.<br>
                Les icônes de pièces SVG sont utilisées avec permission.
            </p>
        </div>
        """.replace("{python_version}", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"))
        layout.addWidget(desc)
        
        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("Fermer")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #e0e0e0;
            }
            QTextBrowser {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14919b;
            }
        """)

