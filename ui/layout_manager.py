"""
Layout Manager for ChessAvatar
Allows users to customize and save different UI layouts
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from PyQt6.QtCore import QSettings


class LayoutConfig:
    """Represents a UI layout configuration"""
    
    def __init__(self, name: str = "Default"):
        self.name = name
        self.splitter_sizes = [1200, 400]  # Main splitter
        self.panels_visible = {
            'engine': True,
            'opening': True,
            'notation': True,
            'clock': True,
            'avatar_status': True,
            'game_controls': True,
        }
        self.panels_positions = {
            'engine': 'bottom_left',
            'opening': 'bottom_left',
            'notation': 'right',
            'clock': 'right',
            'avatar_status': 'right_top',
            'game_controls': 'right_bottom',
        }
        self.board_size = 'auto'  # 'auto', 'small', 'medium', 'large'
        self.notation_height_percent = 40  # % of right panel
        
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'splitter_sizes': self.splitter_sizes,
            'panels_visible': self.panels_visible,
            'panels_positions': self.panels_positions,
            'board_size': self.board_size,
            'notation_height_percent': self.notation_height_percent,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LayoutConfig':
        """Create from dictionary"""
        layout = cls(data.get('name', 'Custom'))
        layout.splitter_sizes = data.get('splitter_sizes', [1200, 400])
        layout.panels_visible = data.get('panels_visible', layout.panels_visible)
        layout.panels_positions = data.get('panels_positions', layout.panels_positions)
        layout.board_size = data.get('board_size', 'auto')
        layout.notation_height_percent = data.get('notation_height_percent', 40)
        return layout


class LayoutManager:
    """Manages UI layouts"""
    
    # Preset layouts
    PRESETS = {
        'default': {
            'name': 'Défaut',
            'description': 'Layout standard avec tous les panels',
            'splitter_sizes': [1200, 400],
            'panels_visible': {
                'engine': True,
                'opening': True,
                'notation': True,
                'clock': True,
                'avatar_status': True,
                'game_controls': True,
            },
        },
        'analysis': {
            'name': 'Analyse',
            'description': 'Optimisé pour l\'analyse (engine et notation)',
            'splitter_sizes': [1000, 600],
            'panels_visible': {
                'engine': True,
                'opening': True,
                'notation': True,
                'clock': False,
                'avatar_status': False,
                'game_controls': True,
            },
        },
        'minimalist': {
            'name': 'Minimaliste',
            'description': 'Juste l\'échiquier et la notation',
            'splitter_sizes': [1300, 300],
            'panels_visible': {
                'engine': False,
                'opening': False,
                'notation': True,
                'clock': False,
                'avatar_status': False,
                'game_controls': True,
            },
        },
        'training': {
            'name': 'Entraînement',
            'description': 'Focus sur l\'échiquier avec pendule',
            'splitter_sizes': [1400, 200],
            'panels_visible': {
                'engine': False,
                'opening': False,
                'notation': True,
                'clock': True,
                'avatar_status': False,
                'game_controls': True,
            },
        },
        'tournament': {
            'name': 'Tournoi',
            'description': 'Comme en tournoi (pendule proéminente)',
            'splitter_sizes': [1100, 500],
            'panels_visible': {
                'engine': False,
                'opening': False,
                'notation': True,
                'clock': True,
                'avatar_status': True,
                'game_controls': True,
            },
        },
    }
    
    def __init__(self, config_dir: Path = None):
        """
        Initialize layout manager
        
        Args:
            config_dir: Directory to store custom layouts
        """
        if config_dir is None:
            config_dir = Path.home() / '.chessavatar' / 'layouts'
        
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.custom_layouts: Dict[str, LayoutConfig] = {}
        self.current_layout: Optional[LayoutConfig] = None
        
        # Load custom layouts
        self.load_custom_layouts()
        
        # Load last used layout
        self.current_layout = self.load_last_layout()
        
    def get_preset_names(self) -> List[str]:
        """Get list of preset layout names"""
        return list(self.PRESETS.keys())
    
    def get_preset(self, name: str) -> Optional[LayoutConfig]:
        """Get a preset layout"""
        preset_data = self.PRESETS.get(name)
        if not preset_data:
            return None
        
        layout = LayoutConfig(preset_data['name'])
        layout.splitter_sizes = preset_data['splitter_sizes']
        layout.panels_visible = preset_data['panels_visible']
        return layout
    
    def get_custom_names(self) -> List[str]:
        """Get list of custom layout names"""
        return list(self.custom_layouts.keys())
    
    def get_all_layouts(self) -> Dict[str, LayoutConfig]:
        """Get all layouts (presets + custom)"""
        layouts = {}
        
        # Add presets
        for name in self.get_preset_names():
            layouts[name] = self.get_preset(name)
        
        # Add custom
        layouts.update(self.custom_layouts)
        
        return layouts
    
    def save_layout(self, layout: LayoutConfig, as_custom: bool = True):
        """
        Save a layout
        
        Args:
            layout: Layout to save
            as_custom: If True, save as custom layout
        """
        if as_custom:
            # Save to file
            file_path = self.config_dir / f"{layout.name.lower().replace(' ', '_')}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(layout.to_dict(), f, indent=2)
            
            self.custom_layouts[layout.name] = layout
        
        # Save as last used
        self.save_last_layout(layout)
    
    def load_custom_layouts(self):
        """Load all custom layouts from disk"""
        self.custom_layouts.clear()
        
        for file_path in self.config_dir.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    layout = LayoutConfig.from_dict(data)
                    self.custom_layouts[layout.name] = layout
            except Exception as e:
                print(f"ERROR: Failed to load layout {file_path}: {e}")
    
    def delete_layout(self, name: str) -> bool:
        """
        Delete a custom layout
        
        Args:
            name: Layout name
            
        Returns:
            True if deleted successfully
        """
        if name not in self.custom_layouts:
            return False
        
        # Delete file
        file_path = self.config_dir / f"{name.lower().replace(' ', '_')}.json"
        if file_path.exists():
            file_path.unlink()
        
        # Remove from memory
        del self.custom_layouts[name]
        return True
    
    def save_last_layout(self, layout: LayoutConfig):
        """Save the last used layout"""
        settings = QSettings('ChessAvatar', 'LayoutManager')
        settings.setValue('last_layout', layout.to_dict())
    
    def load_last_layout(self) -> LayoutConfig:
        """Load the last used layout"""
        settings = QSettings('ChessAvatar', 'LayoutManager')
        data = settings.value('last_layout')
        
        if data:
            try:
                return LayoutConfig.from_dict(data)
            except:
                pass
        
        # Return default
        return self.get_preset('default')
    
    def apply_layout(self, layout: LayoutConfig):
        """Set as current layout"""
        self.current_layout = layout
        self.save_last_layout(layout)
    
    def get_current_layout(self) -> LayoutConfig:
        """Get current layout"""
        if not self.current_layout:
            self.current_layout = self.load_last_layout()
        return self.current_layout
    
    def export_layout(self, layout: LayoutConfig, file_path: Path):
        """Export layout to file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(layout.to_dict(), f, indent=2)
    
    def import_layout(self, file_path: Path) -> Optional[LayoutConfig]:
        """Import layout from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return LayoutConfig.from_dict(data)
        except Exception as e:
            print(f"ERROR: Failed to import layout: {e}")
            return None

