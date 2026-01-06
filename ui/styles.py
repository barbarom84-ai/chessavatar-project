"""
Dynamic dark modern theme styling for the application
Scales based on screen resolution
"""


def get_scaled_theme() -> str:
    """Get theme CSS with scaled font sizes and margins"""
    # Import here to avoid circular dependency and QApplication issues
    try:
        from ui.resolution_manager import get_resolution_manager
        res_mgr = get_resolution_manager()
        
        # Scale base font sizes
        base_font = res_mgr.scale_font(10)
        small_font = res_mgr.scale_font(9)
        large_font = res_mgr.scale_font(12)
        title_font = res_mgr.scale_font(14)
        
        # Scale paddings and margins
        small_pad = res_mgr.scale(4)
        medium_pad = res_mgr.scale(6)
        large_pad = res_mgr.scale(12)
        
        scroll_width = res_mgr.scale(12)
        scroll_radius = res_mgr.scale(6)
        checkbox_size = res_mgr.scale(18)
        radio_size = res_mgr.scale(18)
        radio_radius = res_mgr.scale(9)
        group_margin = res_mgr.scale(10)
        
    except Exception:
        # Fallback to default values if resolution manager fails
        base_font = 10
        small_font = 9
        large_font = 12
        title_font = 14
        small_pad = 4
        medium_pad = 6
        large_pad = 12
        scroll_width = 12
        scroll_radius = 6
        checkbox_size = 18
        radio_size = 18
        radio_radius = 9
        group_margin = 10
    
    return f"""
QMainWindow {{
    background-color: #1e1e1e;
    color: #d4d4d4;
    font-size: {base_font}pt;
}}

QMenuBar {{
    background-color: #2d2d2d;
    color: #d4d4d4;
    border-bottom: 1px solid #3e3e3e;
    padding: {small_pad}px;
    font-size: {base_font}pt;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: {medium_pad}px {large_pad}px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: #3e3e3e;
}}

QMenuBar::item:pressed {{
    background-color: #4e4e4e;
}}

QMenu {{
    background-color: #2d2d2d;
    color: #d4d4d4;
    border: 1px solid #3e3e3e;
    padding: {small_pad}px;
    font-size: {base_font}pt;
}}

QMenu::item {{
    padding: {medium_pad}px 30px {medium_pad}px 20px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: #3e3e3e;
}}

QMenu::separator {{
    height: 1px;
    background: #3e3e3e;
    margin: {small_pad}px 0px;
}}

QPushButton {{
    background-color: #0e639c;
    color: white;
    border: none;
    padding: {medium_pad}px {large_pad}px;
    border-radius: 4px;
    font-weight: bold;
    font-size: {base_font}pt;
}}

QPushButton:hover {{
    background-color: #1177bb;
}}

QPushButton:pressed {{
    background-color: #0d5689;
}}

QPushButton:disabled {{
    background-color: #3e3e3e;
    color: #666666;
}}

QLabel {{
    color: #d4d4d4;
    font-size: {base_font}pt;
}}

QTextEdit {{
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #3e3e3e;
    border-radius: 4px;
    padding: {small_pad}px;
    font-size: {small_font}pt;
    font-family: 'Consolas', 'Courier New', monospace;
}}

QLineEdit {{
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #3e3e3e;
    border-radius: 4px;
    padding: {medium_pad}px;
    font-size: {base_font}pt;
}}

QLineEdit:focus {{
    border: 1px solid #0e639c;
}}

QSplitter::handle {{
    background-color: #3e3e3e;
    width: 2px;
}}

QSplitter::handle:hover {{
    background-color: #0e639c;
}}

#chessboard {{
    background-color: #2d2d2d;
    border: 2px solid #3e3e3e;
    border-radius: 8px;
}}

#rightPanel {{
    background-color: #252525;
    border-radius: 8px;
}}

QStatusBar {{
    background-color: #2d2d2d;
    color: #d4d4d4;
    border-top: 1px solid #3e3e3e;
    font-size: {small_font}pt;
}}

QDialog {{
    background-color: #1e1e1e;
    color: #d4d4d4;
    font-size: {base_font}pt;
}}

QListWidget {{
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #3e3e3e;
    border-radius: 4px;
    font-size: {base_font}pt;
}}

QListWidget::item {{
    padding: {medium_pad}px;
    border-radius: 4px;
}}

QListWidget::item:selected {{
    background-color: #0e639c;
}}

QListWidget::item:hover {{
    background-color: #3e3e3e;
}}

QScrollBar:vertical {{
    background: #1e1e1e;
    width: {scroll_width}px;
    border-radius: {scroll_radius}px;
}}

QScrollBar::handle:vertical {{
    background: #3e3e3e;
    border-radius: {scroll_radius}px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: #4e4e4e;
}}

QScrollBar:horizontal {{
    background: #1e1e1e;
    height: {scroll_width}px;
    border-radius: {scroll_radius}px;
}}

QScrollBar::handle:horizontal {{
    background: #3e3e3e;
    border-radius: {scroll_radius}px;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background: #4e4e4e;
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    border: none;
    background: none;
}}

QScrollBar::add-page, QScrollBar::sub-page {{
    background: none;
}}

QComboBox {{
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #3e3e3e;
    border-radius: 4px;
    padding: {medium_pad}px;
    font-size: {base_font}pt;
}}

QComboBox:hover {{
    border: 1px solid #0e639c;
}}

QComboBox::drop-down {{
    border: none;
    padding-right: {medium_pad}px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #d4d4d4;
    margin-top: 2px;
}}

QTabWidget::pane {{
    border: 1px solid #3e3e3e;
    border-radius: 4px;
    background-color: #1e1e1e;
}}

QTabBar::tab {{
    background-color: #2d2d2d;
    color: #d4d4d4;
    padding: {medium_pad}px {large_pad}px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
    font-size: {base_font}pt;
}}

QTabBar::tab:selected {{
    background-color: #0e639c;
}}

QTabBar::tab:hover {{
    background-color: #3e3e3e;
}}

QGroupBox {{
    border: 1px solid #3e3e3e;
    border-radius: 4px;
    margin-top: {group_margin}px;
    padding-top: {group_margin}px;
    font-size: {base_font}pt;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 {small_pad}px;
    color: #d4d4d4;
    font-weight: bold;
}}

QCheckBox {{
    color: #d4d4d4;
    spacing: {medium_pad}px;
    font-size: {base_font}pt;
}}

QCheckBox::indicator {{
    width: {checkbox_size}px;
    height: {checkbox_size}px;
    border: 2px solid #3e3e3e;
    border-radius: 3px;
    background-color: #1e1e1e;
}}

QCheckBox::indicator:checked {{
    background-color: #0e639c;
    border-color: #0e639c;
}}

QRadioButton {{
    color: #d4d4d4;
    spacing: {medium_pad}px;
    font-size: {base_font}pt;
}}

QRadioButton::indicator {{
    width: {radio_size}px;
    height: {radio_size}px;
    border: 2px solid #3e3e3e;
    border-radius: {radio_radius}px;
    background-color: #1e1e1e;
}}

QRadioButton::indicator:checked {{
    background-color: #0e639c;
    border-color: #0e639c;
}}

QProgressBar {{
    background-color: #1e1e1e;
    border: 1px solid #3e3e3e;
    border-radius: 4px;
    text-align: center;
    font-size: {small_font}pt;
}}

QProgressBar::chunk {{
    background-color: #0e639c;
    border-radius: 3px;
}}

QToolTip {{
    background-color: #2d2d2d;
    color: #d4d4d4;
    border: 1px solid #3e3e3e;
    padding: {small_pad}px;
    border-radius: 4px;
    font-size: {small_font}pt;
}}
"""


# Keep old constant for backward compatibility  
# This will use default values until QApplication is initialized
DARK_THEME = """
QMainWindow {
    background-color: #1e1e1e;
    color: #d4d4d4;
}
"""

