"""
Version information for ChessAvatar
"""

__version__ = "1.0.0"
__author__ = "ChessAvatar Team"
__app_name__ = "ChessAvatar"
__app_name_full__ = "ChessAvatar - Advanced Chess Application"
__description__ = "Modern chess application with AI avatar system"
__copyright__ = "Copyright © 2026 ChessAvatar Team"
__url__ = "https://github.com/chessavatar/chessavatar"

VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION_BUILD = 0

def get_version_string():
    """Get version as string"""
    return f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"

def get_version_tuple():
    """Get version as tuple"""
    return (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, VERSION_BUILD)

