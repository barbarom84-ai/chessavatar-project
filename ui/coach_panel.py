"""
AI Coach panel widget
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTextEdit, QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import chess
from core.ai_coach import get_ai_coach


class CoachPanel(QWidget):
    """Panel showing AI coach hints and advice"""
    
    # Signal emitted when user requests a hint
    hint_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.coach = get_ai_coach()
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("🤖 Coach IA")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Enable/Disable checkbox
        self.enable_checkbox = QCheckBox("Activer les conseils")
        self.enable_checkbox.setChecked(False)
        self.enable_checkbox.stateChanged.connect(self.on_enable_changed)
        layout.addWidget(self.enable_checkbox)
        
        # Advice display
        self.advice_text = QTextEdit()
        self.advice_text.setReadOnly(True)
        self.advice_text.setMaximumHeight(150)
        self.advice_text.setPlaceholderText("Les conseils du coach apparaîtront ici...")
        layout.addWidget(self.advice_text)
        
        # Hint button
        self.hint_button = QPushButton("💡 Demander un conseil")
        self.hint_button.clicked.connect(self.on_hint_requested)
        self.hint_button.setEnabled(False)
        layout.addWidget(self.hint_button)
        
        # Statistics (optional)
        self.stats_label = QLabel("")
        self.stats_label.setWordWrap(True)
        self.stats_label.setStyleSheet("font-size: 9pt; color: #888;")
        layout.addWidget(self.stats_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 8px;
                color: #e0e0e0;
                font-size: 10pt;
            }
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14919b;
            }
            QPushButton:pressed {
                background-color: #0a5a5d;
            }
            QPushButton:disabled {
                background-color: #3c3c3c;
                color: #666;
            }
            QCheckBox {
                color: #e0e0e0;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                background-color: #1e1e1e;
            }
            QCheckBox::indicator:checked {
                background-color: #0d7377;
                border-color: #0d7377;
            }
        """)
        
    def on_enable_changed(self, state):
        """Handle enable/disable checkbox"""
        enabled = (state == Qt.CheckState.Checked.value)
        self.coach.enable_hints(enabled)
        self.hint_button.setEnabled(enabled)
        
        if enabled:
            self.advice_text.setPlainText("✅ Coach IA activé! Cliquez sur 'Demander un conseil' pour obtenir des conseils.")
        else:
            self.advice_text.setPlainText("❌ Coach IA désactivé")
            
    def on_hint_requested(self):
        """Handle hint request"""
        self.hint_requested.emit()
        
    def show_hint(self, hint_text: str):
        """Display a hint"""
        self.advice_text.setPlainText(hint_text)
        
    def show_analysis(self, analysis: dict):
        """Display full position analysis"""
        text = "📊 Analyse de la position:\n\n"
        
        if analysis.get('eval_score') is not None:
            score = analysis['eval_score']
            text += f"Évaluation: {score:+.2f}\n"
            
        if analysis.get('position_type'):
            phase = {
                'opening': 'Ouverture',
                'middlegame': 'Milieu de jeu',
                'endgame': 'Finale'
            }.get(analysis['position_type'], 'Inconnue')
            text += f"Phase: {phase}\n\n"
            
        if analysis.get('strategic_advice'):
            text += "💡 Conseils stratégiques:\n"
            for advice in analysis['strategic_advice']:
                text += f"  • {advice}\n"
            text += "\n"
            
        if analysis.get('threats'):
            text += "⚠️ Menaces:\n"
            for threat in analysis['threats'][:3]:
                text += f"  • {threat}\n"
            text += "\n"
            
        if analysis.get('opportunities'):
            text += "🎯 Opportunités:\n"
            for opp in analysis['opportunities'][:3]:
                text += f"  • {opp}\n"
                
        self.advice_text.setPlainText(text)
        
    def update_stats(self, stats: dict):
        """Update statistics display"""
        if stats:
            text = f"Position: {stats.get('phase', 'N/A')}"
            if stats.get('material_advantage'):
                text += f" | Avantage matériel: {stats['material_advantage']}"
            self.stats_label.setText(text)
        else:
            self.stats_label.setText("")

