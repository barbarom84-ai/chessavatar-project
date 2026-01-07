"""
Chessmaster Theme Manager
Manages piece sets and board themes from Chessmaster Grandmaster Edition
"""
import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ChessmasterTheme:
    """Represents a Chessmaster theme"""
    id: str
    name: str
    category: str  # "wood", "metal", "glass", "cartoon", "historic", "special"
    dat_file: str
    bmp_preview: str
    description: str = ""
    available: bool = True


class ChessmasterThemeManager:
    """Manager for Chessmaster themes"""
    
    def __init__(self, chessmaster_path: str = r"C:\Program Files (x86)\Ubisoft\Chessmaster Grandmaster Edition"):
        """
        Initialize theme manager
        
        Args:
            chessmaster_path: Path to Chessmaster installation
        """
        self.chessmaster_path = chessmaster_path
        self.dat_path = os.path.join(chessmaster_path, "Data", "Dat")
        self.bmp_path = os.path.join(self.dat_path, "BMP")
        self.themes: Dict[str, ChessmasterTheme] = {}
        self.themes_file = "chessmaster_themes.json"
        
        self._discover_themes()
    
    def _discover_themes(self):
        """Discover all available Chessmaster themes"""
        # Check if Chessmaster is installed
        if not os.path.exists(self.dat_path):
            print(f"Chessmaster not found at: {self.chessmaster_path}")
            return
        
        # Define theme categories
        theme_definitions = [
            # WOOD THEMES
            ("staunton_wood", "Staunton Wood", "wood", "A0R_Staunton Wood.dat", "Classic Staunton design in wood"),
            ("classic_wood", "Classic Wood", "wood", "A0R_Classic wood.dat", "Traditional wooden pieces"),
            ("classic_old_wood", "Classic Old Wood", "wood", "A0R_Classic old wood.dat", "Antique wooden pieces"),
            ("indian_wood", "Indian Wood", "wood", "A0F_Indian wood.dat", "Indian style wooden pieces"),
            
            # METAL THEMES
            ("staunton_metal", "Staunton Metal", "metal", "A2R_Staunton metal.dat", "Staunton design in metal"),
            ("fancy_metal", "Fancy Metal", "metal", "A2R_Fancy metal.dat", "Decorative metal pieces"),
            ("irish_metal", "Irish Metal", "metal", "A2R_Irish metal.dat", "Irish style metal pieces"),
            ("steel", "Steel", "metal", "A2R_Steel.dat", "Modern steel pieces"),
            ("classic_metal", "Classic Metal", "metal", "A2R_Classic metal.dat", "Traditional metal pieces"),
            ("anna_metal", "Anna Metal", "metal", "A2F_Anna metal.dat", "Anna design in metal"),
            
            # GLASS THEMES
            ("staunton_glass", "Staunton Glass", "glass", "A3R_Staunton glass.dat", "Transparent glass Staunton"),
            ("fancy_glass", "Fancy Glass", "glass", "A3R_Fancy glass.dat", "Decorative glass pieces"),
            ("irish_glass", "Irish Glass", "glass", "A3R_Irish glass.dat", "Irish style glass pieces"),
            ("classic_glass", "Classic Glass", "glass", "A3F_Classic glass.dat", "Traditional glass pieces"),
            ("indian_glass", "Indian Glass", "glass", "A3F_Indian glass.dat", "Indian style glass pieces"),
            ("anna_glass", "Anna Glass", "glass", "A3F_Anna glass.dat", "Anna design in glass"),
            
            # MARBLE/STONE THEMES
            ("staunton_marble", "Staunton Marble", "marble", "A0R_Staunton marble.dat", "Marble Staunton pieces"),
            ("irish_marble", "Irish Marble", "marble", "A0R_Irish marble.dat", "Irish style marble pieces"),
            ("anna_marble", "Anna Marble", "marble", "A0F_Anna marble.dat", "Anna design in marble"),
            ("fancy_ceramic", "Fancy Ceramic", "marble", "A0R_Fancy ceramic.dat", "Decorative ceramic pieces"),
            
            # HISTORIC THEMES
            ("lewis", "Lewis Chessmen", "historic", "A0F_Lewis.dat", "Iconic Viking chess pieces (12th century)"),
            ("mongol", "Mongol", "historic", "A0F_Mongol.dat", "Mongolian style pieces"),
            ("calvert", "Calvert", "historic", "A0F_Calvert.dat", "Calvert collection pieces"),
            
            # HISTORIC HOUSE OF STAUNTON (HOS)
            ("hos_zagreb", "HOS Zagreb", "historic", "A0F_HOS_Zagreb.dat", "House of Staunton Zagreb"),
            ("hos_hastings", "HOS Hastings", "historic", "A0F_HOS_Hastings.dat", "House of Staunton Hastings"),
            ("hos_sultan", "HOS Sultan", "historic", "A0F_HOS_Sultan.dat", "House of Staunton Sultan"),
            ("hos_reykjavik", "HOS Reykjavik", "historic", "A0F_HOS_Reykjavik.dat", "House of Staunton Reykjavik"),
            ("hos_parthenon", "HOS Parthenon", "historic", "A0F_HOS_Parthenon.dat", "House of Staunton Parthenon"),
            ("hos_morphy", "HOS Morphy", "historic", "A0F_HOS_Morphy.dat", "House of Staunton Morphy"),
            ("hos_marshall", "HOS Marshall", "historic", "A0F_HOS_Marshall.dat", "House of Staunton Marshall"),
            ("hos_capablanca", "HOS Capablanca", "historic", "A0F_HOS_Capablanca.dat", "House of Staunton Capablanca"),
            ("hos_collector", "HOS Collector", "historic", "A0F_HOS_Collector.dat", "House of Staunton Collector"),
            ("hos_calvert", "HOS Calvert", "historic", "A0F_HOS_Calvert.dat", "House of Staunton Calvert"),
            
            # ARTISTIC/MODERN THEMES
            ("bauhaus", "Bauhaus", "modern", "A2F_Bauhaus.dat", "Bauhaus design style"),
            ("egypt", "Egyptian", "modern", "A2F_Egypt.dat", "Ancient Egyptian theme"),
            ("mechanica", "Mechanica", "modern", "A2F_Mechanica.dat", "Mechanical/industrial style"),
            ("modern", "Modern", "modern", "A3F_Modern.dat", "Modern minimalist design"),
            
            # 2D/FLAT THEMES
            ("expert", "Expert", "2d", "B0_Expert.dat", "Simple 2D expert board"),
            ("expert_ii", "Expert II", "2d", "B0_Expert II.dat", "Enhanced 2D expert board"),
            ("newspaper", "Newspaper", "2d", "B0_Newspaper.dat", "Newspaper print style"),
            ("chalkboard", "Chalkboard", "2d", "B0_Chalkboard.dat", "Chalk on blackboard"),
            ("bw_wood", "B&W Wood", "2d", "B0_B&W wood.dat", "Black and white wood texture"),
            ("bw_metal", "B&W Metal", "2d", "B0_B&W metal.dat", "Black and white metal"),
            ("neon", "Neon", "2d", "B0_Neon.dat", "Neon glow effect"),
            ("old_paper", "Old Paper", "2d", "B0_Old paper.dat", "Aged paper texture"),
            ("paint", "Paint", "2d", "B0_Paint.dat", "Painted style"),
            ("stained_glass", "Stained Glass", "2d", "B0_Stained glass.dat", "Stained glass window"),
            ("cartoon_2d", "Cartoon 2D", "2d", "B0_Cartoon 2D.dat", "Flat cartoon style"),
            
            # CARTOON/FUN THEMES
            ("cartoon", "Cartoon 3D", "cartoon", "A4_Cartoon.dat", "3D cartoon characters"),
            ("rubber", "Rubber", "cartoon", "C0_Rubber.dat", "Rubber toy pieces"),
            ("fairytale", "Fairytale", "cartoon", "C0_Fairytale.dat", "Fairytale characters"),
            ("rabbids", "Raving Rabbids", "cartoon", "C0_Raving Rabbids.dat", "Ubisoft Raving Rabbids"),
            ("clash", "Clash", "cartoon", "D4_Clash.dat", "Battle/clash theme"),
            
            # OFFICIAL STAUNTON
            ("staunton_official", "Staunton Official", "staunton", "A0R_Staunton official.dat", "Official tournament Staunton"),
            ("staunton_official_ii", "Staunton Official II", "staunton", "A0R_Staunton official II.dat", "Official Staunton variant"),
        ]
        
        for theme_id, name, category, dat_file, description in theme_definitions:
            # Check if files exist
            dat_path = os.path.join(self.dat_path, dat_file)
            bmp_name = dat_file.replace(".dat", ".bmp").replace("A0R_", "").replace("A0F_", "").replace("A2R_", "").replace("A2F_", "").replace("A3R_", "").replace("A3F_", "").replace("A4_", "").replace("B0_", "").replace("C0_", "").replace("D4_", "")
            bmp_path = os.path.join(self.bmp_path, bmp_name)
            
            available = os.path.exists(dat_path)
            
            theme = ChessmasterTheme(
                id=theme_id,
                name=name,
                category=category,
                dat_file=dat_file,
                bmp_preview=bmp_name,
                description=description,
                available=available
            )
            
            self.themes[theme_id] = theme
        
        print(f"Discovered {len(self.themes)} Chessmaster themes")
        available_count = sum(1 for t in self.themes.values() if t.available)
        print(f"Available: {available_count} themes")
    
    def get_all_themes(self) -> List[ChessmasterTheme]:
        """Get all themes"""
        return list(self.themes.values())
    
    def get_available_themes(self) -> List[ChessmasterTheme]:
        """Get only available themes"""
        return [t for t in self.themes.values() if t.available]
    
    def get_themes_by_category(self, category: str) -> List[ChessmasterTheme]:
        """Get themes by category"""
        return [t for t in self.themes.values() if t.category == category and t.available]
    
    def get_theme(self, theme_id: str) -> Optional[ChessmasterTheme]:
        """Get specific theme"""
        return self.themes.get(theme_id)
    
    def get_preview_path(self, theme_id: str) -> Optional[str]:
        """Get path to preview image"""
        theme = self.get_theme(theme_id)
        if not theme or not theme.available:
            return None
        
        preview_path = os.path.join(self.bmp_path, theme.bmp_preview)
        if os.path.exists(preview_path):
            return preview_path
        return None
    
    def get_dat_path(self, theme_id: str) -> Optional[str]:
        """Get path to DAT file"""
        theme = self.get_theme(theme_id)
        if not theme or not theme.available:
            return None
        
        dat_path = os.path.join(self.dat_path, theme.dat_file)
        if os.path.exists(dat_path):
            return dat_path
        return None
    
    def save_theme_config(self, theme_id: str):
        """Save current theme to config"""
        config = {"current_theme": theme_id}
        with open(self.themes_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_theme_config(self) -> Optional[str]:
        """Load current theme from config"""
        if os.path.exists(self.themes_file):
            try:
                with open(self.themes_file, 'r') as f:
                    config = json.load(f)
                    return config.get("current_theme")
            except:
                pass
        return None
    
    def export_theme_catalog(self, output_file: str = "chessmaster_themes_catalog.json"):
        """Export full catalog of themes"""
        catalog = []
        for theme in self.get_available_themes():
            catalog.append({
                "id": theme.id,
                "name": theme.name,
                "category": theme.category,
                "description": theme.description,
                "dat_file": theme.dat_file,
                "preview": theme.bmp_preview
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(catalog)} themes to {output_file}")


# Global instance
_chessmaster_theme_manager = None

def get_chessmaster_theme_manager() -> ChessmasterThemeManager:
    """Get global theme manager instance"""
    global _chessmaster_theme_manager
    if _chessmaster_theme_manager is None:
        _chessmaster_theme_manager = ChessmasterThemeManager()
    return _chessmaster_theme_manager


if __name__ == "__main__":
    # Test
    manager = ChessmasterThemeManager()
    
    print("\n" + "="*60)
    print("CHESSMASTER THEMES CATALOG")
    print("="*60)
    
    categories = {}
    for theme in manager.get_available_themes():
        if theme.category not in categories:
            categories[theme.category] = []
        categories[theme.category].append(theme)
    
    for category, themes in sorted(categories.items()):
        print(f"\n{category.upper()} ({len(themes)} themes):")
        for theme in sorted(themes, key=lambda t: t.name):
            status = "OK" if theme.available else "N/A"
            print(f"  [{status}] {theme.name:30} - {theme.description}")
    
    # Export catalog
    manager.export_theme_catalog()

