"""
Game report dialog - detailed analysis of a completed game
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTextEdit, QTabWidget, QWidget,
                              QScrollArea, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import chess
from typing import Optional, List, Dict
from core.game import ChessGame
from datetime import datetime


class GameReportDialog(QDialog):
    """Dialog showing detailed game report"""
    
    def __init__(self, game: ChessGame, parent=None):
        super().__init__(parent)
        self.game = game
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Rapport de Partie")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("📊 Rapport d'Analyse de Partie")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab 1: Overview
        tabs.addTab(self._create_overview_tab(), "Vue d'ensemble")
        
        # Tab 2: Move Analysis
        tabs.addTab(self._create_moves_tab(), "Analyse des coups")
        
        # Tab 3: Statistics
        tabs.addTab(self._create_stats_tab(), "Statistiques")
        
        # Tab 4: PGN Export
        tabs.addTab(self._create_pgn_tab(), "Export PGN")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #e0e0e0;
            }
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #e0e0e0;
                padding: 8px 16px;
                border: 1px solid #555;
            }
            QTabBar::tab:selected {
                background-color: #0d7377;
            }
            QTextEdit, QScrollArea {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #3c3c3c;
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
            QGroupBox {
                color: #e0e0e0;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 5px;
            }
        """)
        
    def _create_overview_tab(self) -> QWidget:
        """Create overview tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Game info
        info_group = QGroupBox("Informations de la partie")
        info_layout = QVBoxLayout()
        
        # Result
        result = "En cours"
        if self.game.board.is_game_over():
            if self.game.board.is_checkmate():
                winner = "Blancs" if not self.game.board.turn else "Noirs"
                result = f"Mat - Victoire des {winner}"
            elif self.game.board.is_stalemate():
                result = "Pat - Nulle"
            elif self.game.board.is_insufficient_material():
                result = "Matériel insuffisant - Nulle"
            else:
                result = "Nulle"
        
        info_layout.addWidget(QLabel(f"<b>Résultat:</b> {result}"))
        info_layout.addWidget(QLabel(f"<b>Nombre de coups:</b> {len(self.game.move_history)}"))
        info_layout.addWidget(QLabel(f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}"))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Position info
        pos_group = QGroupBox("Position actuelle")
        pos_layout = QVBoxLayout()
        
        pos_layout.addWidget(QLabel(f"<b>Tour:</b> {'Blancs' if self.game.board.turn else 'Noirs'}"))
        pos_layout.addWidget(QLabel(f"<b>Échec:</b> {'Oui' if self.game.board.is_check() else 'Non'}"))
        
        # Material count
        white_material = self._count_material(chess.WHITE)
        black_material = self._count_material(chess.BLACK)
        pos_layout.addWidget(QLabel(f"<b>Matériel Blancs:</b> {white_material}"))
        pos_layout.addWidget(QLabel(f"<b>Matériel Noirs:</b> {black_material}"))
        pos_layout.addWidget(QLabel(f"<b>Avantage:</b> {abs(white_material - black_material)} ({'Blancs' if white_material > black_material else 'Noirs' if black_material > white_material else 'Égal'})"))
        
        pos_group.setLayout(pos_layout)
        layout.addWidget(pos_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def _create_moves_tab(self) -> QWidget:
        """Create moves analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # Format moves nicely
        moves_text = "<h3>Historique des coups</h3><pre style='font-size: 12pt;'>"
        for i, move in enumerate(self.game.move_history):
            if i % 2 == 0:
                moves_text += f"{i//2 + 1:3d}. {move:8s}"
            else:
                moves_text += f"{move:8s}\n"
        moves_text += "</pre>"
        
        text_edit.setHtml(moves_text)
        layout.addWidget(text_edit)
        
        widget.setLayout(layout)
        return widget
        
    def _create_stats_tab(self) -> QWidget:
        """Create statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        stats_group = QGroupBox("Statistiques de la partie")
        stats_layout = QVBoxLayout()
        
        # Count captures, checks, castling
        captures = sum(1 for move in self.game.move_history if 'x' in move)
        checks = sum(1 for move in self.game.move_history if '+' in move)
        checkmates = sum(1 for move in self.game.move_history if '#' in move)
        castling = sum(1 for move in self.game.move_history if 'O-O' in move)
        
        stats_layout.addWidget(QLabel(f"<b>Captures:</b> {captures}"))
        stats_layout.addWidget(QLabel(f"<b>Échecs:</b> {checks}"))
        stats_layout.addWidget(QLabel(f"<b>Échecs et mat:</b> {checkmates}"))
        stats_layout.addWidget(QLabel(f"<b>Roques:</b> {castling}"))
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def _create_pgn_tab(self) -> QWidget:
        """Create PGN export tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("Export PGN de la partie:")
        layout.addWidget(label)
        
        pgn_edit = QTextEdit()
        pgn_edit.setReadOnly(True)
        pgn_edit.setPlainText(self._generate_pgn())
        layout.addWidget(pgn_edit)
        
        # Copy button
        copy_btn = QPushButton("Copier le PGN")
        copy_btn.clicked.connect(lambda: self._copy_pgn(pgn_edit.toPlainText()))
        layout.addWidget(copy_btn)
        
        widget.setLayout(layout)
        return widget
        
    def _count_material(self, color: chess.Color) -> int:
        """Count material value for a color"""
        values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
        }
        
        total = 0
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            total += len(self.game.board.pieces(piece_type, color)) * values[piece_type]
        
        return total
        
    def _generate_pgn(self) -> str:
        """Generate PGN format"""
        pgn = f"""[Event "Partie ChessAvatar"]
[Date "{datetime.now().strftime('%Y.%m.%d')}"]
[White "Joueur"]
[Black "Adversaire"]
[Result "*"]

{self.game.get_pgn_moves()}
"""
        return pgn
        
    def _copy_pgn(self, text: str):
        """Copy PGN to clipboard"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        # Show confirmation (could use status bar if available)

