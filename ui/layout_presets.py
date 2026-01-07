"""
Predefined layout presets for different use cases
"""
from typing import Dict, Any


class LayoutPresets:
    """Predefined layout configurations"""
    
    @staticmethod
    def get_preset(name: str) -> Dict[str, Any]:
        """Get a preset layout by name"""
        presets = {
            "default": LayoutPresets.default_layout(),
            "minimalist": LayoutPresets.minimalist_layout(),
            "analysis": LayoutPresets.analysis_layout(),
            "training": LayoutPresets.training_layout(),
        }
        return presets.get(name, LayoutPresets.default_layout())
    
    @staticmethod
    def get_all_preset_names():
        """Get all available preset names"""
        return ["default", "minimalist", "analysis", "training"]
    
    @staticmethod
    def default_layout() -> Dict[str, Any]:
        """Default balanced layout"""
        return {
            "name": "Défaut",
            "description": "Disposition équilibrée standard",
            "panels": {
                "engine_panel": True,
                "opening_panel": True,
                "notation_panel": True,
                "avatar_panel": True,
                "stats_panel": True,
            },
            "splitter_sizes": {
                "main": [60, 40],  # Board vs Right panels
                "bottom": [50, 50],  # Engine vs Opening
                "right": [30, 40, 30],  # Notation, Avatar, Stats
            }
        }
    
    @staticmethod
    def minimalist_layout() -> Dict[str, Any]:
        """Minimalist layout - only board and essential info"""
        return {
            "name": "Minimaliste",
            "description": "Échiquier au centre, interface épurée",
            "panels": {
                "engine_panel": False,
                "opening_panel": False,
                "notation_panel": True,
                "avatar_panel": False,
                "stats_panel": False,
            },
            "splitter_sizes": {
                "main": [75, 25],  # More space for board
                "bottom": [0, 0],
                "right": [100, 0, 0],  # Only notation
            }
        }
    
    @staticmethod
    def analysis_layout() -> Dict[str, Any]:
        """Analysis layout - focus on engine and notation"""
        return {
            "name": "Analyse",
            "description": "Optimisé pour l'analyse de parties",
            "panels": {
                "engine_panel": True,
                "opening_panel": True,
                "notation_panel": True,
                "avatar_panel": False,
                "stats_panel": True,
            },
            "splitter_sizes": {
                "main": [55, 45],
                "bottom": [60, 40],  # More space for engine
                "right": [40, 0, 60],  # Notation and Stats
            }
        }
    
    @staticmethod
    def training_layout() -> Dict[str, Any]:
        """Training layout - focus on learning"""
        return {
            "name": "Entraînement",
            "description": "Optimisé pour l'apprentissage",
            "panels": {
                "engine_panel": True,
                "opening_panel": True,
                "notation_panel": True,
                "avatar_panel": True,
                "stats_panel": True,
            },
            "splitter_sizes": {
                "main": [50, 50],  # Equal space
                "bottom": [50, 50],
                "right": [25, 25, 50],  # More space for stats
            }
        }

