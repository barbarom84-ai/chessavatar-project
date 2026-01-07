"""
Resolution Manager for adaptive UI scaling
Automatically adjusts UI elements based on screen resolution
"""
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSize
from typing import Tuple


class ResolutionManager:
    """Manages UI scaling based on screen resolution"""
    
    def __init__(self):
        self.screen = QApplication.primaryScreen()
        self.screen_size = self.screen.size()
        self.screen_dpi = self.screen.logicalDotsPerInch()
        self.scale_factor = self._calculate_scale_factor()
        
    def _calculate_scale_factor(self) -> float:
        """
        Calculate scale factor based on screen resolution
        Base resolution: 1920x1080 (Full HD)
        """
        base_width = 1920
        base_height = 1080
        
        width = self.screen_size.width()
        height = self.screen_size.height()
        
        # Calculate scale based on both dimensions
        width_scale = width / base_width
        height_scale = height / base_height
        
        # Use the smaller scale to ensure everything fits
        scale = min(width_scale, height_scale)
        
        # Clamp between 0.7 and 2.0 for reasonable scaling
        return max(0.7, min(2.0, scale))
    
    def scale(self, value: int) -> int:
        """Scale a value based on screen resolution"""
        return int(value * self.scale_factor)
    
    def scale_font(self, base_size: int) -> int:
        """Scale font size based on screen resolution and DPI"""
        # Adjust for DPI (96 is standard DPI)
        dpi_factor = self.screen_dpi / 96.0
        scaled = base_size * self.scale_factor * dpi_factor
        # Ensure minimum readable size
        return max(8, int(scaled))
    
    def get_board_size(self) -> int:
        """Get optimal chess board size for current resolution"""
        # Base size: 480 pixels (60 * 8) - More compact
        base_board_size = 480
        scaled_size = self.scale(base_board_size)
        
        # Ensure it fits on screen with margins (more conservative)
        max_width = self.screen_size.width() * 0.45  # 45% of screen width
        max_height = self.screen_size.height() * 0.55  # 55% of screen height
        
        return int(min(scaled_size, max_width, max_height))
    
    def get_square_size(self) -> int:
        """Get optimal square size for chess board"""
        board_size = self.get_board_size()
        return board_size // 8
    
    def get_piece_font_size(self) -> int:
        """Get optimal font size for chess pieces"""
        square_size = self.get_square_size()
        # Piece should be about 70-80% of square size
        return int(square_size * 0.75)
    
    def get_window_size(self) -> Tuple[int, int]:
        """Get optimal window size for current resolution"""
        width = self.screen_size.width()
        height = self.screen_size.height()
        
        # Use 90% of screen size for windowed mode (more space for panels)
        optimal_width = int(width * 0.90)
        optimal_height = int(height * 0.88)
        
        # Minimum size: 1400x800 (larger to accommodate all panels)
        optimal_width = max(1400, optimal_width)
        optimal_height = max(800, optimal_height)
        
        return (optimal_width, optimal_height)
    
    def get_engine_panel_height(self) -> int:
        """Get optimal height for engine panel"""
        # Base height: 400-450px
        base_height = 425
        scaled = self.scale(base_height)
        
        # Ensure it doesn't take too much vertical space
        max_height = int(self.screen_size.height() * 0.25)  # Max 25% of screen
        
        return min(scaled, max_height)
    
    def get_right_panel_width(self) -> int:
        """Get optimal width for right panel"""
        # Base width: 350px
        base_width = 350
        scaled = self.scale(base_width)
        
        # Ensure readability
        return max(300, min(500, scaled))
    
    def get_spacing(self, base: int = 10) -> int:
        """Get scaled spacing"""
        return max(5, self.scale(base))
    
    def get_margin(self, base: int = 10) -> int:
        """Get scaled margin"""
        return max(5, self.scale(base))
    
    def get_icon_size(self, base: int = 24) -> int:
        """Get scaled icon size"""
        return max(16, self.scale(base))
    
    def print_info(self):
        """Print resolution information (for debugging)"""
        print(f"Screen Resolution: {self.screen_size.width()}x{self.screen_size.height()}")
        print(f"Screen DPI: {self.screen_dpi}")
        print(f"Scale Factor: {self.scale_factor:.2f}")
        print(f"Board Size: {self.get_board_size()}px")
        print(f"Square Size: {self.get_square_size()}px")
        print(f"Window Size: {self.get_window_size()}")


# Global instance
_resolution_manager = None


def get_resolution_manager() -> ResolutionManager:
    """Get global resolution manager instance"""
    global _resolution_manager
    if _resolution_manager is None:
        _resolution_manager = ResolutionManager()
    return _resolution_manager


def reset_resolution_manager():
    """Reset resolution manager (useful when screen changes)"""
    global _resolution_manager
    _resolution_manager = None

