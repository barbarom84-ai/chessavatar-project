"""
Chess clock widget for time control
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont


# Time control presets (seconds, increment)
TIME_CONTROLS = {
    "Bullet 1+0": (60, 0),
    "Bullet 1+1": (60, 1),
    "Bullet 2+1": (120, 1),
    "Blitz 3+0": (180, 0),
    "Blitz 3+2": (180, 2),
    "Blitz 5+0": (300, 0),
    "Blitz 5+3": (300, 3),
    "Rapid 10+0": (600, 0),
    "Rapid 10+5": (600, 5),
    "Rapid 15+10": (900, 10),
    "Classical 30+0": (1800, 0),
    "Classical 30+20": (1800, 20),
    "Classical 60+0": (3600, 0),
    "Sans limite": (999999, 0),
}


class ClockWidget(QWidget):
    """Widget displaying chess clocks for both players"""
    
    time_expired = pyqtSignal(str)  # Émet 'white' ou 'black'
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initial_white_time = 600  # 10 minutes in seconds
        self.initial_black_time = 600
        self.white_time = 600
        self.black_time = 600
        self.increment = 0  # Incrément en secondes
        self.active_color = None  # 'white' or 'black'
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        self.title_label = QLabel("⏱ Pendule")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)
        
        # Time control selector
        control_layout = QHBoxLayout()
        control_label = QLabel("Cadence:")
        control_label.setStyleSheet("font-size: 9pt; color: #888888;")
        self.time_control_combo = QComboBox()
        self.time_control_combo.setStyleSheet("""
            QComboBox {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 4px;
                font-size: 9pt;
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
        for control_name in TIME_CONTROLS.keys():
            self.time_control_combo.addItem(control_name)
        self.time_control_combo.setCurrentText("Rapid 10+0")
        self.time_control_combo.currentTextChanged.connect(self.on_time_control_changed)
        control_layout.addWidget(control_label)
        control_layout.addWidget(self.time_control_combo)
        layout.addLayout(control_layout)
        
        # Black clock
        black_container = QWidget()
        black_layout = QVBoxLayout(black_container)
        black_layout.setContentsMargins(5, 5, 5, 5)
        
        black_label = QLabel("Noirs")
        black_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.black_time_label = QLabel("10:00")
        self.black_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.black_time_label.setStyleSheet("""
            QLabel {
                font-size: 24pt;
                font-weight: bold;
                background-color: #1e1e1e;
                border: 2px solid #3e3e3e;
                border-radius: 8px;
                padding: 15px;
                color: #d4d4d4;
            }
        """)
        black_layout.addWidget(black_label)
        black_layout.addWidget(self.black_time_label)
        layout.addWidget(black_container)
        
        # White clock
        white_container = QWidget()
        white_layout = QVBoxLayout(white_container)
        white_layout.setContentsMargins(5, 5, 5, 5)
        
        white_label = QLabel("Blancs")
        white_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.white_time_label = QLabel("10:00")
        self.white_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.white_time_label.setStyleSheet("""
            QLabel {
                font-size: 24pt;
                font-weight: bold;
                background-color: #1e1e1e;
                border: 2px solid #3e3e3e;
                border-radius: 8px;
                padding: 15px;
                color: #d4d4d4;
            }
        """)
        white_layout.addWidget(white_label)
        white_layout.addWidget(self.white_time_label)
        layout.addWidget(white_container)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("▶ Démarrer")
        self.pause_button = QPushButton("⏸ Pause")
        self.reset_button = QPushButton("↻ Réinitialiser")
        
        self.pause_button.setEnabled(False)
        
        self.start_button.clicked.connect(self.start)
        self.pause_button.clicked.connect(self.pause)
        self.reset_button.clicked.connect(self.reset)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.reset_button)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        
    def set_time(self, white_seconds: int, black_seconds: int):
        """Set initial time for both players"""
        self.white_time = white_seconds
        self.black_time = black_seconds
        self.update_display()
        
    def update_display(self):
        """Update time display"""
        self.white_time_label.setText(self.format_time(self.white_time))
        self.black_time_label.setText(self.format_time(self.black_time))
        
        # Highlight active clock
        if self.active_color == 'white':
            self.white_time_label.setStyleSheet("""
                QLabel {
                    font-size: 24pt;
                    font-weight: bold;
                    background-color: #0e639c;
                    border: 2px solid #1177bb;
                    border-radius: 8px;
                    padding: 15px;
                    color: #ffffff;
                }
            """)
            self.black_time_label.setStyleSheet("""
                QLabel {
                    font-size: 24pt;
                    font-weight: bold;
                    background-color: #1e1e1e;
                    border: 2px solid #3e3e3e;
                    border-radius: 8px;
                    padding: 15px;
                    color: #d4d4d4;
                }
            """)
        elif self.active_color == 'black':
            self.black_time_label.setStyleSheet("""
                QLabel {
                    font-size: 24pt;
                    font-weight: bold;
                    background-color: #0e639c;
                    border: 2px solid #1177bb;
                    border-radius: 8px;
                    padding: 15px;
                    color: #ffffff;
                }
            """)
            self.white_time_label.setStyleSheet("""
                QLabel {
                    font-size: 24pt;
                    font-weight: bold;
                    background-color: #1e1e1e;
                    border: 2px solid #3e3e3e;
                    border-radius: 8px;
                    padding: 15px;
                    color: #d4d4d4;
                }
            """)
        else:
            self.white_time_label.setStyleSheet("""
                QLabel {
                    font-size: 24pt;
                    font-weight: bold;
                    background-color: #1e1e1e;
                    border: 2px solid #3e3e3e;
                    border-radius: 8px;
                    padding: 15px;
                    color: #d4d4d4;
                }
            """)
            self.black_time_label.setStyleSheet("""
                QLabel {
                    font-size: 24pt;
                    font-weight: bold;
                    background-color: #1e1e1e;
                    border: 2px solid #3e3e3e;
                    border-radius: 8px;
                    padding: 15px;
                    color: #d4d4d4;
                }
            """)
        
    def format_time(self, seconds: int) -> str:
        """Format seconds as MM:SS"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
        
    def update_time(self):
        """Update the active clock"""
        if self.active_color == 'white':
            self.white_time -= 1
            if self.white_time <= 0:
                self.white_time = 0
                self.timer.stop()
                self.white_time_label.setText("00:00 - Temps écoulé!")
                self.time_expired.emit('white')  # Émission du signal
        elif self.active_color == 'black':
            self.black_time -= 1
            if self.black_time <= 0:
                self.black_time = 0
                self.timer.stop()
                self.black_time_label.setText("00:00 - Temps écoulé!")
                self.time_expired.emit('black')  # Émission du signal
        
        self.update_display()
        
    def switch_clock(self):
        """Switch active clock and add increment"""
        # Add increment to player who just moved
        if self.active_color == 'white':
            self.white_time += self.increment
            self.active_color = 'black'
        elif self.active_color == 'black':
            self.black_time += self.increment
            self.active_color = 'white'
        else:
            self.active_color = 'white'
        
        self.update_display()
        
    def start(self):
        """Start the clock"""
        if not self.active_color:
            self.active_color = 'white'
        self.timer.start(1000)  # Update every second
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.update_display()
        
    def pause(self):
        """Pause the clock"""
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        
    def reset(self):
        """Reset the clock"""
        self.timer.stop()
        self.white_time = self.initial_white_time
        self.black_time = self.initial_black_time
        self.active_color = None
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.update_display()
    
    def set_time_control(self, time_seconds: int, increment: int = 0):
        """Set time control for both players"""
        self.initial_white_time = time_seconds
        self.initial_black_time = time_seconds
        self.white_time = time_seconds
        self.black_time = time_seconds
        self.increment = increment
        self.update_display()
    
    def on_time_control_changed(self, control_name: str):
        """Handle time control change"""
        if control_name in TIME_CONTROLS:
            time_seconds, increment = TIME_CONTROLS[control_name]
            self.set_time_control(time_seconds, increment)
            
            # Update title with increment info
            if increment > 0:
                self.title_label.setText(f"⏱ Pendule (+{increment}s)")
            else:
                self.title_label.setText("⏱ Pendule")
            
            print(f"DEBUG: Cadence changée à {control_name} ({time_seconds}s + {increment}s)")

