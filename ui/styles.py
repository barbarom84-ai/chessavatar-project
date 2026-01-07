"""
Global Stylesheet for ChessAvatar
Provides consistent styling across the application
"""

# Color Palette
COLORS = {
    'background': '#1e1e1e',
    'surface': '#252526',
    'surface_light': '#2d2d30',
    'border': '#3e3e3e',
    'border_hover': '#555555',
    'text': '#d4d4d4',
    'text_secondary': '#888888',
    'accent': '#0e639c',
    'accent_hover': '#1177bb',
    'accent_pressed': '#0d5689',
    'success': '#0e7d06',
    'success_hover': '#0f9607',
    'warning': '#f0ad4e',
    'danger': '#d9534f',
    'highlight': '#094771',
}

# Font Settings
FONTS = {
    'title': 'font-family: "Segoe UI", Arial, sans-serif; font-size: 14pt; font-weight: bold;',
    'subtitle': 'font-family: "Segoe UI", Arial, sans-serif; font-size: 12pt; font-weight: 600;',
    'body': 'font-family: "Segoe UI", Arial, sans-serif; font-size: 10pt;',
    'button': 'font-family: "Segoe UI", Arial, sans-serif; font-size: 10pt; font-weight: 500;',
    'mono': 'font-family: "Consolas", "Monaco", "Courier New", monospace; font-size: 10pt;',
}


def get_main_stylesheet():
    """Get the main application stylesheet"""
    return f"""
    /* Main Window */
    QMainWindow {{
        background-color: {COLORS['background']};
        color: {COLORS['text']};
    }}
    
    /* Menu Bar */
    QMenuBar {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        border-bottom: 1px solid {COLORS['border']};
        padding: 4px;
        {FONTS['body']}
    }}
    
    QMenuBar::item {{
        background-color: transparent;
        padding: 6px 12px;
        border-radius: 4px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {COLORS['accent']};
    }}
    
    QMenuBar::item:pressed {{
        background-color: {COLORS['accent_pressed']};
    }}
    
    /* Menu Dropdown */
    QMenu {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        padding: 8px 0px;
        {FONTS['body']}
    }}
    
    QMenu::item {{
        padding: 8px 24px 8px 12px;
        margin: 2px 4px;
        border-radius: 4px;
    }}
    
    QMenu::item:selected {{
        background-color: {COLORS['accent']};
    }}
    
    QMenu::separator {{
        height: 1px;
        background-color: {COLORS['border']};
        margin: 6px 8px;
    }}
    
    QMenu::icon {{
        padding-left: 8px;
    }}
    
    /* Status Bar */
    QStatusBar {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        border-top: 1px solid {COLORS['border']};
        {FONTS['body']}
        padding: 4px;
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {COLORS['surface_light']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        padding: 8px 16px;
        {FONTS['button']}
        min-height: 32px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['accent']};
        border-color: {COLORS['accent_hover']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['accent_pressed']};
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS['surface']};
        color: {COLORS['text_secondary']};
        border-color: {COLORS['border']};
    }}
    
    /* Primary Button */
    QPushButton[primary="true"] {{
        background-color: {COLORS['accent']};
        color: white;
        border: none;
    }}
    
    QPushButton[primary="true"]:hover {{
        background-color: {COLORS['accent_hover']};
    }}
    
    QPushButton[primary="true"]:pressed {{
        background-color: {COLORS['accent_pressed']};
    }}
    
    /* Success Button */
    QPushButton[success="true"] {{
        background-color: {COLORS['success']};
        color: white;
        border: none;
    }}
    
    QPushButton[success="true"]:hover {{
        background-color: {COLORS['success_hover']};
    }}
    
    /* Danger Button */
    QPushButton[danger="true"] {{
        background-color: {COLORS['danger']};
        color: white;
        border: none;
    }}
    
    QPushButton[danger="true"]:hover {{
        background-color: #c9302c;
    }}
    
    /* Group Boxes */
    QGroupBox {{
        {FONTS['subtitle']}
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 18px;
        color: {COLORS['text']};
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px;
        background-color: {COLORS['background']};
    }}
    
    /* Labels */
    QLabel {{
        color: {COLORS['text']};
        {FONTS['body']}
    }}
    
    /* Panels */
    QWidget#rightPanel {{
        background-color: {COLORS['surface']};
        border-left: 1px solid {COLORS['border']};
    }}
    
    /* Splitter */
    QSplitter::handle {{
        background-color: {COLORS['border']};
    }}
    
    QSplitter::handle:horizontal {{
        width: 3px;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 {COLORS['surface']},
                                    stop:0.5 {COLORS['border']},
                                    stop:1 {COLORS['surface']});
        margin: 0px 1px;
    }}
    
    QSplitter::handle:vertical {{
        height: 3px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLORS['surface']},
                                    stop:0.5 {COLORS['border']},
                                    stop:1 {COLORS['surface']});
        margin: 1px 0px;
    }}
    
    QSplitter::handle:hover {{
        background-color: {COLORS['accent']};
    }}
    
    QSplitter::handle:horizontal:hover {{
        background: {COLORS['accent']};
        width: 4px;
    }}
    
    QSplitter::handle:vertical:hover {{
        background: {COLORS['accent']};
        height: 4px;
    }}
    
    /* Scroll Bars */
    QScrollBar:vertical {{
        background-color: {COLORS['surface']};
        width: 12px;
        border: none;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['border_hover']};
        border-radius: 6px;
        min-height: 30px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['accent']};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background-color: {COLORS['surface']};
        height: 12px;
        border: none;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {COLORS['border_hover']};
        border-radius: 6px;
        min-width: 30px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {COLORS['accent']};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    /* Tooltips */
    QToolTip {{
        background-color: {COLORS['surface_light']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px;
        {FONTS['body']}
    }}
    """


def get_panel_style():
    """Get style for side panels"""
    return f"""
        QWidget {{
            background-color: {COLORS['surface']};
            color: {COLORS['text']};
            border-radius: 8px;
            padding: 12px;
        }}
    """


def get_button_style(button_type='default'):
    """
    Get button style
    
    Args:
        button_type: 'default', 'primary', 'success', 'danger', 'warning'
    """
    base = f"""
        QPushButton {{
            {FONTS['button']}
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            min-height: 36px;
        }}
    """
    
    if button_type == 'primary':
        return base + f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['accent_pressed']};
            }}
        """
    elif button_type == 'success':
        return base + f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
            }}
            QPushButton:hover {{
                background-color: {COLORS['success_hover']};
            }}
        """
    elif button_type == 'danger':
        return base + f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                color: white;
            }}
            QPushButton:hover {{
                background-color: #c9302c;
            }}
        """
    elif button_type == 'warning':
        return base + f"""
            QPushButton {{
                background-color: {COLORS['warning']};
                color: #222;
            }}
            QPushButton:hover {{
                background-color: #ec971f;
            }}
        """
    else:  # default
        return base + f"""
            QPushButton {{
                background-color: {COLORS['surface_light']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent']};
                border-color: {COLORS['accent']};
                color: white;
            }}
            QPushButton:pressed {{
                background-color: {COLORS['accent_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_secondary']};
            }}
        """


def get_title_style(size='normal'):
    """Get title label style"""
    font = FONTS['title'] if size == 'large' else FONTS['subtitle']
    return f"""
        QLabel {{
            {font}
            color: {COLORS['text']};
            padding: 8px;
        }}
    """
