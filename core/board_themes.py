"""
Board Themes for ChessAvatar
Pre-defined color schemes for the chessboard
"""
from PyQt6.QtGui import QColor


class BoardTheme:
    """Represents a board color theme"""
    
    def __init__(self, name: str, light_color: str, dark_color: str, 
                 description: str = "", highlight_color: str = "#FFFF00"):
        """
        Initialize a board theme
        
        Args:
            name: Theme name
            light_color: Color for light squares (hex)
            dark_color: Color for dark squares (hex)
            description: Theme description
            highlight_color: Color for highlights (hex)
        """
        self.name = name
        self.light_color = QColor(light_color)
        self.dark_color = QColor(dark_color)
        self.highlight_color = QColor(highlight_color)
        self.description = description
        
    def to_dict(self) -> dict:
        """Convert theme to dictionary"""
        return {
            'name': self.name,
            'light': self.light_color.name(),
            'dark': self.dark_color.name(),
            'highlight': self.highlight_color.name(),
            'description': self.description
        }
        
    @staticmethod
    def from_dict(data: dict) -> 'BoardTheme':
        """Create theme from dictionary"""
        return BoardTheme(
            name=data.get('name', 'Custom'),
            light_color=data.get('light', '#F0D9B5'),
            dark_color=data.get('dark', '#B58863'),
            description=data.get('description', ''),
            highlight_color=data.get('highlight', '#FFFF00')
        )


# Pre-defined themes
THEMES = {
    "classic": BoardTheme(
        name="Classique",
        light_color="#F0D9B5",
        dark_color="#B58863",
        description="Thème classique marron clair/foncé"
    ),
    
    "blue": BoardTheme(
        name="Bleu",
        light_color="#DEE3E6",
        dark_color="#8CA2AD",
        description="Thème bleu élégant"
    ),
    
    "green": BoardTheme(
        name="Vert",
        light_color="#FFFFDD",
        dark_color="#86A666",
        description="Thème vert naturel"
    ),
    
    "wood": BoardTheme(
        name="Bois",
        light_color="#D4B483",
        dark_color="#8B5A3C",
        description="Aspect bois réaliste 3D",
        highlight_color="#FFD700"
    ),
    
    "minimal": BoardTheme(
        name="Minimaliste",
        light_color="#F0F0F0",
        dark_color="#D0D0D0",
        description="Design épuré moderne",
        highlight_color="#4A9EFF"
    ),
    
    "colorblind": BoardTheme(
        name="Daltonien",
        light_color="#F5D76E",
        dark_color="#4A90E2",
        description="Optimisé pour daltonisme (jaune/bleu)",
        highlight_color="#FF6B6B"
    ),
    
    "high_contrast": BoardTheme(
        name="Contraste Élevé",
        light_color="#FFFFFF",
        dark_color="#000000",
        description="Contraste maximum noir & blanc",
        highlight_color="#FF0000"
    ),
    
    "purple": BoardTheme(
        name="Violet",
        light_color="#E8D7F1",
        dark_color="#9B72AA",
        description="Thème violet élégant"
    ),
    
    "brown": BoardTheme(
        name="Marron",
        light_color="#EAD8C4",
        dark_color="#9A7456",
        description="Tons marron chauds"
    ),
    
    "ice": BoardTheme(
        name="Glace",
        light_color="#E8F4F8",
        dark_color="#B0C4DE",
        description="Bleu glacé rafraîchissant"
    ),
    
    "neon": BoardTheme(
        name="Néon",
        light_color="#1A1A1A",
        dark_color="#0D0D0D",
        description="Thème sombre avec accents néon",
        highlight_color="#00FF00"
    ),
    
    "cherry": BoardTheme(
        name="Cerise",
        light_color="#FFE4E1",
        dark_color="#DC143C",
        description="Rouge cerise dynamique"
    ),
    
    "ocean": BoardTheme(
        name="Océan",
        light_color="#E0F2F7",
        dark_color="#006994",
        description="Bleu océan profond"
    ),
    
    "earth": BoardTheme(
        name="Terre",
        light_color="#DEB887",
        dark_color="#8B4513",
        description="Tons terre naturels"
    ),
    
    "tournament": BoardTheme(
        name="Tournoi",
        light_color="#EEEED2",
        dark_color="#769656",
        description="Standard de tournoi officiel (chess.com)"
    ),
    
    "lichess": BoardTheme(
        name="Lichess",
        light_color="#F0D9B5",
        dark_color="#B58863",
        description="Thème par défaut Lichess"
    ),
}


def get_theme(name: str) -> BoardTheme:
    """
    Get a theme by name
    
    Args:
        name: Theme name
        
    Returns:
        BoardTheme object
    """
    return THEMES.get(name.lower(), THEMES["classic"])


def get_all_theme_names() -> list:
    """Get list of all available theme names"""
    return list(THEMES.keys())


def get_all_themes() -> dict:
    """Get dictionary of all themes"""
    return THEMES.copy()


class BoardThemes:
    """Utility class for accessing board themes"""
    
    @staticmethod
    def get_theme(name: str) -> dict:
        """
        Get a theme by name as a dictionary
        
        Args:
            name: Theme name
            
        Returns:
            Dictionary with 'light', 'dark', 'highlight', etc.
        """
        theme = get_theme(name)
        return theme.to_dict()
    
    @staticmethod
    def get_all_names() -> list:
        """Get list of all theme names"""
        return get_all_theme_names()


