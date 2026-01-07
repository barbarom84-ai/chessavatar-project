"""
Engine analysis panel with evaluation bar and principal variations
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from typing import Optional, Dict, List


class EvaluationBar(QWidget):
    """Visual evaluation bar showing position assessment"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.evaluation = 0.0  # In pawns, positive = white advantage
        self.is_mate = False
        self.mate_in = 0
        self.setMinimumHeight(400)
        self.setMaximumWidth(40)
        
    def set_evaluation(self, eval_cp: Optional[int] = None, mate_in: Optional[int] = None):
        """
        Set the evaluation
        
        Args:
            eval_cp: Evaluation in centipawns (from white's perspective)
            mate_in: Mate in N moves (positive = white mates, negative = black mates)
        """
        if mate_in is not None:
            self.is_mate = True
            self.mate_in = mate_in
            # Max out the bar for mate
            self.evaluation = 10.0 if mate_in > 0 else -10.0
        elif eval_cp is not None:
            self.is_mate = False
            # Convert centipawns to pawns
            self.evaluation = eval_cp / 100.0
            # Clamp to reasonable range for display
            self.evaluation = max(-10.0, min(10.0, self.evaluation))
        
        self.update()
        
    def paintEvent(self, event):
        """Paint the evaluation bar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Calculate white percentage (0-1)
        # eval +5 = 100% white, -5 = 0% white (100% black)
        white_percentage = (self.evaluation + 10.0) / 20.0
        white_percentage = max(0.0, min(1.0, white_percentage))
        
        white_height = int(height * white_percentage)
        black_height = height - white_height
        
        # Draw black portion (top)
        painter.fillRect(0, 0, width, black_height, QColor("#2c2c2c"))
        
        # Draw white portion (bottom)
        painter.fillRect(0, black_height, width, white_height, QColor("#e8e8e8"))
        
        # Draw border
        painter.setPen(QPen(QColor("#3e3e3e"), 2))
        painter.drawRect(1, 1, width - 2, height - 2)
        
        # Draw center line
        center_y = height // 2
        painter.setPen(QPen(QColor("#0e639c"), 2))
        painter.drawLine(0, center_y, width, center_y)
        
        # Draw evaluation text
        painter.setPen(QColor("#d4d4d4"))
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        
        if self.is_mate:
            text = f"M{abs(self.mate_in)}"
        else:
            text = f"{abs(self.evaluation):.1f}"
            
        # Position text in the larger section
        text_y = black_height // 2 if black_height > white_height else black_height + white_height // 2
        painter.drawText(0, text_y, width, 20, Qt.AlignmentFlag.AlignCenter, text)


class PrincipalVariationWidget(QWidget):
    """Widget displaying principal variations from engine"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.variations: List[Dict] = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Title
        title = QLabel("Meilleures lignes")
        title.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(title)
        
        # Text display for variations
        self.pv_text = QTextEdit()
        self.pv_text.setReadOnly(True)
        self.pv_text.setMaximumHeight(150)
        self.pv_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.pv_text)
        
    def update_variations(self, variations: List[Dict]):
        """
        Update principal variations
        
        Args:
            variations: List of variation dicts with 'score', 'mate', 'pv' keys
        """
        self.variations = variations
        
        # Format text
        text_lines = []
        for i, var in enumerate(variations, 1):
            # Format score
            if var.get("mate") is not None:
                score_str = f"M{var['mate']}"
            elif var.get("score") is not None:
                score = var["score"] / 100.0
                score_str = f"{score:+.2f}"
            else:
                score_str = "..."
                
            # Format moves
            moves = " ".join(var.get("pv", [])[:8])  # Show first 8 moves
            if len(var.get("pv", [])) > 8:
                moves += " ..."
                
            text_lines.append(f"{i}. [{score_str}] {moves}")
            
        self.pv_text.setPlainText("\n".join(text_lines))
        
    def clear(self):
        """Clear variations"""
        self.variations = []
        self.pv_text.clear()


class EnginePanel(QWidget):
    """Complete engine analysis panel"""
    
    # Signals
    start_analysis = pyqtSignal()
    stop_analysis = pyqtSignal()
    option_changed = pyqtSignal(str, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_analyzing = False
        self.current_depth = 0
        self.current_nodes = 0
        self.current_threads = 1
        self.variations_data: Dict[int, Dict] = {}  # multipv -> data
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Title and status
        header_layout = QVBoxLayout()  # Changed to vertical for better layout
        header_layout.setSpacing(5)
        
        title = QLabel("⚙ Moteur d'Analyse")
        title.setStyleSheet("font-weight: bold; font-size: 13pt; color: #4FC3F7;")
        header_layout.addWidget(title)
        
        self.engine_status = QLabel("Aucun moteur")
        self.engine_status.setStyleSheet("""
            QLabel {
                color: #888888; 
                font-size: 10pt;
                padding: 4px 8px;
                background-color: #1e1e1e;
                border-left: 3px solid #888888;
                border-radius: 3px;
            }
        """)
        header_layout.addWidget(self.engine_status)
        
        main_layout.addLayout(header_layout)
        
        # UCI Configuration display
        uci_group = QGroupBox("Configuration")
        uci_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 10pt;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        uci_layout = QVBoxLayout(uci_group)
        uci_layout.setSpacing(8)
        
        # Threads control row
        threads_row = QHBoxLayout()
        threads_row.setSpacing(8)
        
        threads_label_static = QLabel("Threads:")
        threads_label_static.setStyleSheet("font-size: 10pt; color: #d4d4d4; font-weight: bold;")
        threads_row.addWidget(threads_label_static)
        
        self.threads_label = QLabel("--")
        self.threads_label.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                color: #4FC3F7;
                font-weight: bold;
                padding: 2px 8px;
                background-color: #1e1e1e;
                border-radius: 3px;
                min-width: 30px;
            }
        """)
        threads_row.addWidget(self.threads_label)
        
        btn_style = """
            QPushButton {
                background-color: #3e3e3e;
                color: #d4d4d4;
                border: 1px solid #555555;
                border-radius: 3px;
                min-width: 24px;
                min-height: 24px;
                max-width: 24px;
                max-height: 24px;
                font-size: 12pt;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #4e4e4e;
                border-color: #4FC3F7;
            }
            QPushButton:pressed {
                background-color: #2e2e2e;
            }
            QPushButton:disabled {
                color: #555555;
                background-color: #2a2a2a;
                border-color: #333333;
            }
        """
        
        self.minus_thread_btn = QPushButton("-")
        self.minus_thread_btn.setStyleSheet(btn_style)
        self.minus_thread_btn.setToolTip("Diminuer le nombre de threads")
        self.minus_thread_btn.clicked.connect(self._on_decrease_threads)
        self.minus_thread_btn.setEnabled(False)
        threads_row.addWidget(self.minus_thread_btn)
        
        self.plus_thread_btn = QPushButton("+")
        self.plus_thread_btn.setStyleSheet(btn_style)
        self.plus_thread_btn.setToolTip("Augmenter le nombre de threads")
        self.plus_thread_btn.clicked.connect(self._on_increase_threads)
        self.plus_thread_btn.setEnabled(False)
        threads_row.addWidget(self.plus_thread_btn)
        
        threads_row.addStretch()
        uci_layout.addLayout(threads_row)
        
        # Hash row
        hash_row = QHBoxLayout()
        hash_row.setSpacing(8)
        
        hash_label_static = QLabel("Hash:")
        hash_label_static.setStyleSheet("font-size: 10pt; color: #d4d4d4; font-weight: bold;")
        hash_row.addWidget(hash_label_static)
        
        self.hash_label = QLabel("--")
        self.hash_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #4FC3F7;
                font-weight: bold;
                padding: 2px 8px;
                background-color: #1e1e1e;
                border-radius: 3px;
            }
        """)
        hash_row.addWidget(self.hash_label)
        hash_row.addStretch()
        uci_layout.addLayout(hash_row)
        
        main_layout.addWidget(uci_group)
        
        # Evaluation bar and PV container
        eval_container = QHBoxLayout()
        
        # Evaluation bar
        self.eval_bar = EvaluationBar()
        eval_container.addWidget(self.eval_bar)
        
        # Evaluation info
        eval_info_layout = QVBoxLayout()
        
        # Numeric evaluation
        self.eval_label = QLabel("0.00")
        self.eval_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.eval_label.setStyleSheet("""
            QLabel {
                font-size: 20pt;
                font-weight: bold;
                background-color: #1e1e1e;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 10px;
                color: #d4d4d4;
            }
        """)
        eval_info_layout.addWidget(self.eval_label)
        
        # Analysis info - more compact and cleaner
        info_row = QHBoxLayout()
        info_row.setSpacing(10)
        
        self.depth_label = QLabel("Prof: --")
        self.depth_label.setStyleSheet("font-size: 10pt; color: #888888;")
        info_row.addWidget(self.depth_label)
        
        self.nodes_label = QLabel("Nœuds: --")
        self.nodes_label.setStyleSheet("font-size: 10pt; color: #888888;")
        info_row.addWidget(self.nodes_label)
        
        self.nps_label = QLabel("N/s: --")
        self.nps_label.setStyleSheet("font-size: 10pt; color: #888888;")
        info_row.addWidget(self.nps_label)
        
        info_row.addStretch()
        eval_info_layout.addLayout(info_row)
        
        eval_info_layout.addStretch()
        eval_container.addLayout(eval_info_layout, stretch=1)
        
        main_layout.addLayout(eval_container)
        
        # Principal variations
        self.pv_widget = PrincipalVariationWidget()
        main_layout.addWidget(self.pv_widget)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.analyze_button = QPushButton("▶ Analyser")
        self.analyze_button.clicked.connect(self._on_analyze_clicked)
        button_layout.addWidget(self.analyze_button)
        
        self.stop_button = QPushButton("⏹ Arrêter")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        button_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
    def set_engine_status(self, engine_name: str, uci_options: Optional[Dict] = None):
        """Set engine status and UCI parameters"""
        self.engine_status.setText(f"🔹 {engine_name}")
        self.engine_status.setStyleSheet("""
            QLabel {
                color: #4FC3F7; 
                font-size: 10pt;
                font-weight: bold;
                padding: 4px 8px;
                background-color: #1e1e1e;
                border-left: 3px solid #4FC3F7;
                border-radius: 3px;
            }
        """)
        self.analyze_button.setEnabled(True)
        
        # Display UCI parameters
        if uci_options:
            threads = uci_options.get("Threads", 1)
            hash_mb = uci_options.get("Hash", "--")
            
            # Handle the case where threads might be a string or None
            try:
                self.current_threads = int(threads)
            except (ValueError, TypeError):
                self.current_threads = 1
                
            self.threads_label.setText(f"{self.current_threads}")
            self.hash_label.setText(f"{hash_mb} MB")
            
            self.minus_thread_btn.setEnabled(True)
            self.plus_thread_btn.setEnabled(True)
        else:
            self.threads_label.setText("--")
            self.hash_label.setText("--")
            self.minus_thread_btn.setEnabled(False)
            self.plus_thread_btn.setEnabled(False)
        
    def clear_engine_status(self):
        """Clear engine status"""
        self.engine_status.setText("Aucun moteur")
        self.engine_status.setStyleSheet("color: #888888; font-size: 9pt;")
        self.analyze_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.minus_thread_btn.setEnabled(False)
        self.plus_thread_btn.setEnabled(False)
    
    def _on_increase_threads(self):
        """Increase thread count"""
        import os
        max_threads = os.cpu_count() or 64
        if self.current_threads < max_threads:
            self.current_threads += 1
            self.threads_label.setText(f"Threads: {self.current_threads}")
            self.option_changed.emit("Threads", self.current_threads)
            
    def _on_decrease_threads(self):
        """Decrease thread count"""
        if self.current_threads > 1:
            self.current_threads -= 1
            self.threads_label.setText(f"Threads: {self.current_threads}")
            self.option_changed.emit("Threads", self.current_threads)
            
    def update_analysis(self, data: Dict):
        """
        Update analysis display
        
        Args:
            data: Analysis data dict with score, depth, pv, etc.
        """
        multipv = data.get("multipv", 1)
        self.variations_data[multipv] = data
        
        # Update for first variation (main line)
        if multipv == 1:
            # Update evaluation bar and label
            if data.get("mate") is not None:
                self.eval_bar.set_evaluation(mate_in=data["mate"])
                self.eval_label.setText(f"Mat en {abs(data['mate'])}")
                if data["mate"] > 0:
                    self.eval_label.setStyleSheet("""
                        QLabel {
                            font-size: 20pt;
                            font-weight: bold;
                            background-color: #1e1e1e;
                            border: 2px solid #00ff00;
                            border-radius: 4px;
                            padding: 10px;
                            color: #00ff00;
                        }
                    """)
                else:
                    self.eval_label.setStyleSheet("""
                        QLabel {
                            font-size: 20pt;
                            font-weight: bold;
                            background-color: #1e1e1e;
                            border: 2px solid #ff0000;
                            border-radius: 4px;
                            padding: 10px;
                            color: #ff0000;
                        }
                    """)
            elif data.get("score") is not None:
                score = data["score"]
                self.eval_bar.set_evaluation(eval_cp=score)
                self.eval_label.setText(f"{score/100.0:+.2f}")
                self.eval_label.setStyleSheet("""
                    QLabel {
                        font-size: 20pt;
                        font-weight: bold;
                        background-color: #1e1e1e;
                        border: 1px solid #3e3e3e;
                        border-radius: 4px;
                        padding: 10px;
                        color: #d4d4d4;
                    }
                """)
                
            # Update info labels
            self.depth_label.setText(f"Profondeur: {data.get('depth', 0)}")
            
            nodes = data.get('nodes', 0)
            if nodes > 1_000_000:
                self.nodes_label.setText(f"Nœuds: {nodes/1_000_000:.1f}M")
            elif nodes > 1_000:
                self.nodes_label.setText(f"Nœuds: {nodes/1_000:.1f}K")
            else:
                self.nodes_label.setText(f"Nœuds: {nodes}")
                
            nps = data.get('nps', 0)
            if nps > 1_000_000:
                self.nps_label.setText(f"N/s: {nps/1_000_000:.1f}M")
            elif nps > 1_000:
                self.nps_label.setText(f"N/s: {nps/1_000:.1f}K")
            else:
                self.nps_label.setText(f"N/s: {nps}")
                
        # Update principal variations
        variations = sorted(self.variations_data.values(), key=lambda x: x.get("multipv", 1))
        self.pv_widget.update_variations(variations)
        
    def _on_analyze_clicked(self):
        """Handle analyze button click"""
        print("DEBUG: EnginePanel._on_analyze_clicked appele")
        print(f"DEBUG: is_analyzing avant: {self.is_analyzing}")
        self.is_analyzing = True
        self.analyze_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.variations_data.clear()
        print("DEBUG: Emission du signal start_analysis")
        self.start_analysis.emit()
        print(f"DEBUG: is_analyzing apres: {self.is_analyzing}")
        
    def _on_stop_clicked(self):
        """Handle stop button click"""
        self.is_analyzing = False
        self.analyze_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.stop_analysis.emit()
        
    def reset_analysis(self):
        """Reset analysis display"""
        self.eval_bar.set_evaluation(eval_cp=0)
        self.eval_label.setText("0.00")
        self.eval_label.setStyleSheet("""
            QLabel {
                font-size: 20pt;
                font-weight: bold;
                background-color: #1e1e1e;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 10px;
                color: #d4d4d4;
            }
        """)
        self.depth_label.setText("Profondeur: --")
        self.nodes_label.setText("Nœuds: --")
        self.nps_label.setText("N/s: --")
        self.pv_widget.clear()
        self.variations_data.clear()
        
        if self.is_analyzing:
            self._on_stop_clicked()

