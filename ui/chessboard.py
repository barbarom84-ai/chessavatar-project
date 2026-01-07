"""
2D Chess board widget with drag and drop functionality
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QPixmap, QPen, QBrush, QMouseEvent, QFont, QWheelEvent
import chess
from typing import Optional, List
from ui.resolution_manager import get_resolution_manager
from core.board_themes import BoardThemes
from core.svg_pieces import SVGPieces
from ui.promotion_dialog import PromotionDialog


class ChessBoardWidget(QWidget):
    """Interactive 2D chess board widget with zoom and pan support"""
    
    # Signal emitted when a move is made (from_square, to_square)
    move_made = pyqtSignal(int, int)
    # Signal emitted when zoom level changes
    zoom_changed = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chessboard")
        self.board = chess.Board()
        
        # Get optimal sizes from resolution manager
        self.res_mgr = get_resolution_manager()
        self.square_size = self.res_mgr.get_square_size()
        self.board_size = self.square_size * 8
        self.piece_font_size = self.res_mgr.get_piece_font_size()
        
        # Theme and piece set
        self.current_theme = "classic"
        self.piece_set = "svg"  # Use SVG by default (ChessAvatar pieces)
        self.svg_pieces = SVGPieces("chessavatar", self.square_size)  # ChessAvatar set
        
        # Colors (will be updated by set_theme)
        self.light_square = QColor("#f0d9b5")
        self.dark_square = QColor("#b58863")
        self.highlight_color = QColor("#646f40")
        self.selected_color = QColor("#829769")
        self.legal_move_color = QColor("#546e7a")
        
        # Apply default theme
        self.set_theme(self.current_theme)
        
        # Interaction state
        self.selected_square: Optional[int] = None
        self.legal_moves: List[chess.Move] = []
        self.dragging = False
        self.drag_piece: Optional[chess.Piece] = None
        self.drag_pos = QPoint()
        self.from_square: Optional[int] = None
        
        # Flip board (False = white at bottom)
        self.flipped = False
        
        # Zoom and pan support
        self.zoom_factor = 1.0  # 1.0 = 100%
        self.min_zoom = 0.5     # 50% minimum
        self.max_zoom = 2.0     # 200% maximum
        self.pan_offset = QPoint(0, 0)
        self.pan_mode = False  # Toggle for pan mode
        self.pan_dragging = False
        self.pan_start_pos = QPoint()
        self.pan_start_offset = QPoint()
        
        # Evaluation bar (integrated)
        self.evaluation_cp = 0  # Centipawns (positive = white advantage)
        self.evaluation_mate = None  # Mate in X moves
        self.eval_bar_width = 20  # Width of evaluation bar
        
        # Control buttons visibility
        self.controls_visible = False
        self.control_button_size = 30
        
        # Calculate margins based on resolution
        self.margin = self.res_mgr.get_margin(30)
        min_size = self.board_size + self.margin * 2
        self.setMinimumSize(min_size, min_size)
        self.setMouseTracking(True)
        
        # Unicode chess pieces
        self.piece_symbols = {
            chess.PAWN: {'white': '♙', 'black': '♟'},
            chess.KNIGHT: {'white': '♘', 'black': '♞'},
            chess.BISHOP: {'white': '♗', 'black': '♝'},
            chess.ROOK: {'white': '♖', 'black': '♜'},
            chess.QUEEN: {'white': '♕', 'black': '♛'},
            chess.KING: {'white': '♔', 'black': '♚'},
        }
    
    def hasHeightForWidth(self) -> bool:
        """Widget maintains aspect ratio"""
        return True
    
    def heightForWidth(self, width: int) -> int:
        """Return height for given width to maintain square aspect ratio"""
        return width
    
    def sizeHint(self):
        """Provide size hint for layout"""
        from PyQt6.QtCore import QSize
        size = self.board_size + self.margin * 2
        return QSize(size, size)
        
    def set_board(self, board: chess.Board):
        """Set the board position"""
        self.board = board
        self.selected_square = None
        self.legal_moves = []
        self.update()
        
    def flip_board(self):
        """Flip the board orientation"""
        self.flipped = not self.flipped
        self.update()
    
    def set_theme(self, theme_name: str):
        """Set the board theme"""
        self.current_theme = theme_name
        theme_colors = BoardThemes.get_theme(theme_name)
        
        self.light_square = QColor(theme_colors["light"])
        self.dark_square = QColor(theme_colors["dark"])
        self.highlight_color = QColor(theme_colors.get("highlight", "#646f40"))
        self.selected_color = QColor(theme_colors.get("selected", "#829769"))
        self.legal_move_color = QColor(theme_colors.get("legal_move", "#546e7a"))
        
        self.update()
    
    def set_piece_set(self, piece_set: str):
        """Set the piece set (default or svg)"""
        self.piece_set = piece_set
        self.update()
        
    def set_evaluation(self, eval_cp: Optional[int] = None, mate_in: Optional[int] = None):
        """
        Set evaluation for the integrated eval bar
        
        Args:
            eval_cp: Evaluation in centipawns (positive = white advantage)
            mate_in: Mate in X moves (positive = white mates, negative = black mates)
        """
        if mate_in is not None:
            self.evaluation_mate = mate_in
            self.evaluation_cp = 0
        else:
            self.evaluation_cp = eval_cp if eval_cp is not None else 0
            self.evaluation_mate = None
        self.update()
    
    def set_controls_visible(self, visible: bool):
        """Show/hide control buttons overlay"""
        self.controls_visible = visible
        self.update()
    
    def set_pan_mode(self, enabled: bool):
        """Enable or disable pan mode"""
        self.pan_mode = enabled
        if enabled:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def set_zoom(self, zoom: float):
        """Set zoom level (0.5 to 2.0)"""
        old_zoom = self.zoom_factor
        self.zoom_factor = max(self.min_zoom, min(self.max_zoom, zoom))
        
        # Update square size based on zoom
        base_square_size = self.res_mgr.get_square_size()
        self.square_size = int(base_square_size * self.zoom_factor)
        self.board_size = self.square_size * 8
        
        # Update SVG pieces size
        if self.piece_set == "svg":
            self.svg_pieces = SVGPieces("chessavatar", self.square_size)
        
        # Adjust piece font size for unicode pieces
        self.piece_font_size = int(self.res_mgr.get_piece_font_size() * self.zoom_factor)
        
        # Emit signal
        self.zoom_changed.emit(self.zoom_factor)
        self.update()
    
    def zoom_in(self):
        """Zoom in by 10%"""
        self.set_zoom(self.zoom_factor + 0.1)
    
    def zoom_out(self):
        """Zoom out by 10%"""
        self.set_zoom(self.zoom_factor - 0.1)
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.set_zoom(1.0)
    
    def reset_pan(self):
        """Reset pan offset to center"""
        self.pan_offset = QPoint(0, 0)
        self.update()
    
    def square_to_coords(self, square: int) -> tuple:
        """Convert chess square to pixel coordinates (with zoom and pan)"""
        if self.flipped:
            file = 7 - chess.square_file(square)
            rank = chess.square_rank(square)
        else:
            file = chess.square_file(square)
            rank = 7 - chess.square_rank(square)
        
        x = self.margin + file * self.square_size + self.pan_offset.x()
        y = self.margin + rank * self.square_size + self.pan_offset.y()
        return (x, y)
        
    def coords_to_square(self, x: int, y: int) -> Optional[int]:
        """Convert pixel coordinates to chess square (with zoom and pan)"""
        x -= self.margin + self.pan_offset.x()
        y -= self.margin + self.pan_offset.y()
        
        if x < 0 or y < 0 or x >= self.board_size or y >= self.board_size:
            return None
            
        file = x // self.square_size
        rank = y // self.square_size
        
        if self.flipped:
            file = 7 - file  # Inverser horizontalement
            # rank reste tel quel (pas de double inversion)
            # Quand flipped, Y pixel et rank vont dans le même sens
        else:
            rank = 7 - rank  # Inverser verticalement pour orientation normale
            
        return chess.square(file, rank)
        
    def paintEvent(self, event):
        """Paint the chess board"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # ===== EVALUATION BAR (Left side, integrated) =====
        self._draw_evaluation_bar(painter)
        
        # Draw board squares
        for square in chess.SQUARES:
            x, y = self.square_to_coords(square)
            
            # Determine square color
            if (chess.square_file(square) + chess.square_rank(square)) % 2 == 0:
                color = self.dark_square
            else:
                color = self.light_square
                
            # Highlight selected square
            if square == self.selected_square:
                color = self.selected_color
            # Highlight legal move destinations
            elif self.selected_square is not None and any(
                move.to_square == square for move in self.legal_moves
            ):
                color = self.legal_move_color
                
            painter.fillRect(x, y, self.square_size, self.square_size, color)
            
        # Draw coordinates with scaled font
        painter.setPen(QColor("#666666"))
        font = QFont()
        coord_font_size = self.res_mgr.scale_font(9)
        font.setPointSize(coord_font_size)
        painter.setFont(font)
        
        coord_margin = self.res_mgr.get_margin(10)
        
        # Files (a-h)
        for file in range(8):
            label = chr(ord('a') + (file if not self.flipped else 7 - file))
            x = self.margin + file * self.square_size + self.square_size // 2 - coord_margin // 2
            y = self.margin + self.board_size + coord_margin + coord_font_size
            painter.drawText(x, y, label)
            
        # Ranks (1-8)
        for rank in range(8):
            label = str((rank if self.flipped else 7 - rank) + 1)
            x = coord_margin
            y = self.margin + rank * self.square_size + self.square_size // 2 + coord_font_size // 2
            painter.drawText(x, y, label)
            
        # Draw pieces
        if self.piece_set == "svg":
            # Use SVG pieces
            for square in chess.SQUARES:
                piece = self.board.piece_at(square)
                if piece and not (self.dragging and square == self.from_square):
                    x, y = self.square_to_coords(square)
                    # Render the piece to a pixmap
                    pixmap = self.svg_pieces.render_piece(piece, self.square_size)
                    painter.drawPixmap(x, y, pixmap)
        else:
            # Use default Unicode pieces
            piece_font = QFont()
            piece_font.setPointSize(self.piece_font_size)
            painter.setFont(piece_font)
            
            for square in chess.SQUARES:
                piece = self.board.piece_at(square)
                if piece and not (self.dragging and square == self.from_square):
                    x, y = self.square_to_coords(square)
                    color_key = 'white' if piece.color == chess.WHITE else 'black'
                    symbol = self.piece_symbols[piece.piece_type][color_key]
                    
                    # Set piece color
                    if piece.color == chess.WHITE:
                        painter.setPen(QColor("#ffffff"))
                    else:
                        painter.setPen(QColor("#000000"))
                        
                    # Center the piece in the square using Qt alignment
                    piece_rect = QRect(x, y, self.square_size, self.square_size)
                    painter.drawText(
                        piece_rect,
                        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                        symbol
                    )
                
        # Draw dragged piece
        if self.dragging and self.drag_piece:
            half_square = self.square_size // 2
            drag_x = self.drag_pos.x() - half_square
            drag_y = self.drag_pos.y() - half_square
            
            if self.piece_set == "svg":
                # Render the dragged piece to a pixmap
                pixmap = self.svg_pieces.render_piece(self.drag_piece, self.square_size)
                painter.drawPixmap(drag_x, drag_y, pixmap)
            else:
                color_key = 'white' if self.drag_piece.color == chess.WHITE else 'black'
                symbol = self.piece_symbols[self.drag_piece.piece_type][color_key]
                
                if self.drag_piece.color == chess.WHITE:
                    painter.setPen(QColor("#ffffff"))
                else:
                    painter.setPen(QColor("#000000"))
                    
                drag_rect = QRect(drag_x, drag_y, self.square_size, self.square_size)
                painter.drawText(
                    drag_rect,
                    Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                    symbol
                )
            
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zoom"""
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Pan mode - drag to move board
            if self.pan_mode:
                self.pan_dragging = True
                self.pan_start_pos = event.pos()
                self.pan_start_offset = QPoint(self.pan_offset)
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                return
            
            # Normal chess piece interaction
            square = self.coords_to_square(event.pos().x(), event.pos().y())
            
            if square is not None:
                piece = self.board.piece_at(square)
                
                # If clicking on own piece, select it
                if piece and piece.color == self.board.turn:
                    self.selected_square = square
                    self.legal_moves = [
                        move for move in self.board.legal_moves
                        if move.from_square == square
                    ]
                    self.from_square = square
                    self.drag_piece = piece
                    self.dragging = True
                    self.drag_pos = event.pos()
                    self.update()
                # If clicking on destination square
                elif self.selected_square is not None:
                    self.try_move(self.selected_square, square)
                    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move (dragging or panning)"""
        if self.pan_dragging:
            # Update pan offset
            delta = event.pos() - self.pan_start_pos
            self.pan_offset = self.pan_start_offset + delta
            self.update()
        elif self.dragging:
            self.drag_pos = event.pos()
            self.update()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            # End panning
            if self.pan_dragging:
                self.pan_dragging = False
                self.setCursor(Qt.CursorShape.OpenHandCursor)
                return
            
            # End piece dragging
            if self.dragging:
                self.dragging = False
                to_square = self.coords_to_square(event.pos().x(), event.pos().y())
                
                if to_square is not None and self.from_square is not None:
                    self.try_move(self.from_square, to_square)
                
                self.selected_square = None
                self.legal_moves = []
                self.from_square = None
                self.drag_piece = None
                self.update()
            
    def try_move(self, from_square: int, to_square: int):
        """Try to make a move"""
        # Check if it's a legal move
        move = None
        for legal_move in self.board.legal_moves:
            if legal_move.from_square == from_square and legal_move.to_square == to_square:
                move = legal_move
                break
                
        if move:
            # Handle pawn promotion - ask user
            if move.promotion is None and self.board.piece_at(from_square).piece_type == chess.PAWN:
                if chess.square_rank(to_square) in [0, 7]:
                    # Show promotion dialog
                    dialog = PromotionDialog(self)
                    if dialog.exec():
                        promotion_piece = dialog.get_selected_piece()
                        move = chess.Move(from_square, to_square, promotion_piece)
                    else:
                        # User cancelled - default to queen
                        move = chess.Move(from_square, to_square, chess.QUEEN)
                    
            self.move_made.emit(from_square, to_square)
            
        self.selected_square = None
        self.legal_moves = []
        self.update()
    
    def _draw_evaluation_bar(self, painter: QPainter):
        """Draw the evaluation bar on the left side of the board"""
        # Bar position and size
        bar_x = self.margin - self.eval_bar_width - 5
        bar_y = self.margin + self.pan_offset.y()
        bar_height = self.board_size
        
        if bar_x < 0:
            return  # Not enough space
        
        # Calculate evaluation percentage (0-100, 50 = equal)
        if self.evaluation_mate is not None:
            # Mate situation
            eval_percent = 100 if self.evaluation_mate > 0 else 0
        else:
            # Centipawn evaluation
            # Clamp to +/- 10 pawns (1000 centipawns)
            clamped_eval = max(-1000, min(1000, self.evaluation_cp))
            # Convert to 0-100 scale (50 = equal)
            eval_percent = 50 + (clamped_eval / 1000.0) * 50
        
        # Draw background (full bar)
        painter.fillRect(bar_x, bar_y, self.eval_bar_width, bar_height, QColor("#1e1e1e"))
        
        # Calculate split point
        white_height = int(bar_height * (1 - eval_percent / 100.0))
        black_height = bar_height - white_height
        
        # Draw black advantage (top)
        if black_height > 0:
            painter.fillRect(bar_x, bar_y, self.eval_bar_width, black_height, QColor("#3d3d3d"))
        
        # Draw white advantage (bottom)
        if white_height > 0:
            painter.fillRect(bar_x, bar_y + black_height, self.eval_bar_width, white_height, QColor("#e8e8e8"))
        
        # Draw border
        painter.setPen(QPen(QColor("#555555"), 1))
        painter.drawRect(bar_x, bar_y, self.eval_bar_width, bar_height)
        
        # Draw evaluation text (small, vertical center)
        if self.evaluation_mate is not None:
            eval_text = f"M{abs(self.evaluation_mate)}"
            text_color = QColor("#ffffff") if self.evaluation_mate > 0 else QColor("#000000")
        else:
            eval_value = self.evaluation_cp / 100.0
            if abs(eval_value) < 0.1:
                eval_text = "0.0"
            else:
                eval_text = f"{eval_value:+.1f}"
            # Choose text color based on which side is on top at text position
            text_color = QColor("#000000") if eval_percent > 50 else QColor("#ffffff")
        
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(text_color)
        
        # Draw text at center of bar
        text_rect = QRect(bar_x, bar_y + bar_height // 2 - 20, self.eval_bar_width, 40)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, eval_text)
    
    def _draw_floating_controls(self, painter: QPainter):
        """Draw floating control buttons (zoom, pan, flip) - very discreet"""
        if not self.controls_visible:
            return
        
        # Position: top-right corner of board
        btn_size = self.control_button_size
        padding = 5
        start_x = self.margin + self.board_size - btn_size - padding + self.pan_offset.x()
        start_y = self.margin + padding + self.pan_offset.y()
        
        # Semi-transparent background
        bg_color = QColor(30, 30, 30, 180)  # Dark with transparency
        
        # Draw buttons vertically
        buttons = [
            ("🔍+", "Zoom in"),
            ("🔍-", "Zoom out"),
            ("⟲", "Flip board"),
            ("🖐", "Pan mode" if not self.pan_mode else "Play mode")
        ]
        
        for i, (icon, tooltip) in enumerate(buttons):
            y = start_y + i * (btn_size + padding)
            
            # Background
            painter.fillRect(start_x, y, btn_size, btn_size, bg_color)
            painter.setPen(QPen(QColor("#4FC3F7"), 1))
            painter.drawRect(start_x, y, btn_size, btn_size)
            
            # Icon text
            painter.setPen(QColor("#ffffff"))
            font = QFont()
            font.setPointSize(10)
            painter.setFont(font)
            text_rect = QRect(start_x, y, btn_size, btn_size)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, icon)
                move = legal_move
                break
                
        if move:
            # Handle pawn promotion - ask user
            if move.promotion is None and self.board.piece_at(from_square).piece_type == chess.PAWN:
                if chess.square_rank(to_square) in [0, 7]:
                    # Show promotion dialog
                    dialog = PromotionDialog(self)
                    if dialog.exec():
                        promotion_piece = dialog.get_selected_piece()
                        move = chess.Move(from_square, to_square, promotion_piece)
                    else:
                        # User cancelled - default to queen
                        move = chess.Move(from_square, to_square, chess.QUEEN)
                    
            self.move_made.emit(from_square, to_square)
            
        self.selected_square = None
        self.legal_moves = []
        self.update()

