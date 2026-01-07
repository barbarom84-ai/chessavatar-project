"""
SVG Chess Piece Renderer
Renders chess pieces from SVG files for sharp display at any resolution
"""
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtCore import Qt, QByteArray
import chess
from pathlib import Path
from typing import Dict, Optional


class SVGPieceRenderer:
    """Render chess pieces from SVG files with caching"""
    
    # Available piece sets
    PIECE_SETS = {
        "chessavatar": "ChessAvatar (Default)",  # Our custom SVG set from assets/
        "cburnett": "Lichess Classic",           # Fallback inline SVGs
    }
    
    def __init__(self, piece_set: str = "chessavatar", square_size: int = 70):
        """
        Initialize SVG renderer
        
        Args:
            piece_set: Name of the piece set to use (default: "chessavatar")
            square_size: Size of each square in pixels
        """
        self.piece_set = piece_set
        self.square_size = square_size
        self._cache: Dict[tuple, QPixmap] = {}
        
        # Get assets directory
        self.assets_dir = Path(__file__).parent.parent / "assets"
        
    def _load_svg_from_file(self, piece: chess.Piece) -> Optional[bytes]:
        """
        Load SVG data from file in assets directory
        
        Args:
            piece: Chess piece
            
        Returns:
            SVG data as bytes, or None if file not found
        """
        # Piece character mapping for file names
        piece_chars = {
            chess.PAWN: 'P',
            chess.KNIGHT: 'N',
            chess.BISHOP: 'B',
            chess.ROOK: 'R',
            chess.QUEEN: 'Q',
            chess.KING: 'K'
        }
        
        color = 'W' if piece.color == chess.WHITE else 'B'
        piece_char = piece_chars[piece.piece_type]
        
        # File name format: WP.svg, BK.svg, etc.
        filename = f"{color}{piece_char}.svg"
        filepath = self.assets_dir / filename
        
        if filepath.exists():
            with open(filepath, 'rb') as f:
                return f.read()
        
        return None
    
    def _get_fallback_svg(self, piece: chess.Piece) -> str:
        """
        Get fallback inline SVG for pieces (simple colored circles)
        Used if files are not found
        
        Args:
            piece: Chess piece
            
        Returns:
            SVG data as string
        """
        color = "white" if piece.color == chess.WHITE else "black"
        stroke = "black" if piece.color == chess.WHITE else "white"
        
        # Simple representation with piece symbol
        symbols = {
            chess.PAWN: '♙' if piece.color == chess.WHITE else '♟',
            chess.KNIGHT: '♘' if piece.color == chess.WHITE else '♞',
            chess.BISHOP: '♗' if piece.color == chess.WHITE else '♝',
            chess.ROOK: '♖' if piece.color == chess.WHITE else '♜',
            chess.QUEEN: '♕' if piece.color == chess.WHITE else '♛',
            chess.KING: '♔' if piece.color == chess.WHITE else '♚',
        }
        
        symbol = symbols[piece.piece_type]
        
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">
            <circle cx="22.5" cy="22.5" r="18" fill="{color}" stroke="{stroke}" stroke-width="2"/>
            <text x="22.5" y="30" font-size="24" text-anchor="middle" fill="{stroke}">{symbol}</text>
        </svg>'''
    
    def render_piece(self, piece: chess.Piece, size: Optional[int] = None) -> QPixmap:
        """
        Render a chess piece to a QPixmap
        
        Args:
            piece: Chess piece to render
            size: Size in pixels (uses square_size if None)
            
        Returns:
            QPixmap of the rendered piece
        """
        if size is None:
            size = self.square_size
        
        # Check cache
        cache_key = (piece.piece_type, piece.color, size, self.piece_set)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Create pixmap with padding (reduce piece size by 10%)
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Add 10% padding on each side
        padding = int(size * 0.1)
        render_size = size - (padding * 2)
        
        # Load SVG data
        if self.piece_set == "chessavatar":
            svg_data = self._load_svg_from_file(piece)
            if svg_data:
                # Render from file
                renderer = QSvgRenderer(QByteArray(svg_data))
            else:
                # Fallback if file not found
                print(f"WARNING: SVG file not found for {piece}, using fallback")
                svg_str = self._get_fallback_svg(piece)
                renderer = QSvgRenderer(QByteArray(svg_str.encode('utf-8')))
        else:
            # Use fallback for other sets
            svg_str = self._get_fallback_svg(piece)
            renderer = QSvgRenderer(QByteArray(svg_str.encode('utf-8')))
        
        # Render to pixmap with padding
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        # Render in the center with padding (use QRectF for float coordinates)
        from PyQt6.QtCore import QRectF
        renderer.render(painter, QRectF(padding, padding, render_size, render_size))
        painter.end()
        
        # Cache it
        self._cache[cache_key] = pixmap
        
        return pixmap
        
    def set_piece_set(self, piece_set: str):
        """
        Change the piece set
        
        Args:
            piece_set: Name of the new piece set
        """
        if piece_set != self.piece_set:
            self.piece_set = piece_set
            self._cache.clear()  # Clear cache when changing sets
            
    def set_size(self, size: int):
        """
        Change the size for rendered pieces
        
        Args:
            size: New size in pixels
        """
        if size != self.square_size:
            self.square_size = size
            self._cache.clear()  # Clear cache when changing size
            
    def clear_cache(self):
        """Clear the pixmap cache"""
        self._cache.clear()


# Alias for convenience
SVGPieces = SVGPieceRenderer
