"""
2D Chess board widget with drag and drop functionality
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPixmap, QPen, QBrush, QMouseEvent, QFont
import chess
from typing import Optional, List
from ui.resolution_manager import get_resolution_manager


class ChessBoardWidget(QWidget):
    """Interactive 2D chess board widget"""
    
    # Signal emitted when a move is made (from_square, to_square)
    move_made = pyqtSignal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chessboard")
        self.board = chess.Board()
        
        # Get optimal sizes from resolution manager
        self.res_mgr = get_resolution_manager()
        self.square_size = self.res_mgr.get_square_size()
        self.board_size = self.square_size * 8
        self.piece_font_size = self.res_mgr.get_piece_font_size()
        
        # Colors
        self.light_square = QColor("#f0d9b5")
        self.dark_square = QColor("#b58863")
        self.highlight_color = QColor("#646f40")
        self.selected_color = QColor("#829769")
        self.legal_move_color = QColor("#546e7a")
        
        # Interaction state
        self.selected_square: Optional[int] = None
        self.legal_moves: List[chess.Move] = []
        self.dragging = False
        self.drag_piece: Optional[chess.Piece] = None
        self.drag_pos = QPoint()
        self.from_square: Optional[int] = None
        
        # Flip board (False = white at bottom)
        self.flipped = False
        
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
        
    def square_to_coords(self, square: int) -> tuple:
        """Convert chess square to pixel coordinates"""
        if self.flipped:
            file = 7 - chess.square_file(square)
            rank = chess.square_rank(square)
        else:
            file = chess.square_file(square)
            rank = 7 - chess.square_rank(square)
        
        x = self.margin + file * self.square_size
        y = self.margin + rank * self.square_size
        return (x, y)
        
    def coords_to_square(self, x: int, y: int) -> Optional[int]:
        """Convert pixel coordinates to chess square"""
        x -= self.margin
        y -= self.margin
        
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
            
        # Draw pieces with scaled font
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
            color_key = 'white' if self.drag_piece.color == chess.WHITE else 'black'
            symbol = self.piece_symbols[self.drag_piece.piece_type][color_key]
            
            if self.drag_piece.color == chess.WHITE:
                painter.setPen(QColor("#ffffff"))
            else:
                painter.setPen(QColor("#000000"))
                
            # Center piece around cursor position
            half_square = self.square_size // 2
            drag_rect = QRect(
                self.drag_pos.x() - half_square,
                self.drag_pos.y() - half_square,
                self.square_size,
                self.square_size
            )
            painter.drawText(
                drag_rect,
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                symbol
            )
            
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
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
        """Handle mouse move (dragging)"""
        if self.dragging:
            self.drag_pos = event.pos()
            self.update()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
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
            # Handle pawn promotion (default to queen for now)
            if move.promotion is None and self.board.piece_at(from_square).piece_type == chess.PAWN:
                if chess.square_rank(to_square) in [0, 7]:
                    move = chess.Move(from_square, to_square, chess.QUEEN)
                    
            self.move_made.emit(from_square, to_square)
            
        self.selected_square = None
        self.legal_moves = []
        self.update()

