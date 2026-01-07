"""
Chessmaster Personality Configuration System
Based on TheKing engine parameters from http://utzingerk.com/how_to_use.htm
"""
from dataclasses import dataclass, field
from typing import Dict, Optional
import json
from pathlib import Path


@dataclass
class ChessmasterPersonality:
    """
    Configuration for a Chessmaster/TheKing personality
    
    Based on cm_parm parameters:
    - Material values (own/opponent pieces)
    - Positional factors (center control, mobility, king safety, passed pawns, pawn weakness)
    - Play style (strength, attack/defense, contempt, randomness)
    - Search parameters (selective search, max depth)
    """
    name: str
    description: str = ""
    
    # Opponent's piece values (0-4500 for pawns, 0-1500 for pieces, 0-900 for queen base scale)
    opp_pawn: int = 100  # opp
    opp_knight: int = 100  # opn
    opp_bishop: int = 100  # opb
    opp_rook: int = 100  # opr
    opp_queen: int = 100  # opq
    
    # King's (our) piece values
    my_pawn: int = 100  # myp
    my_knight: int = 100  # myn
    my_bishop: int = 100  # myb
    my_rook: int = 100  # myr
    my_queen: int = 100  # myq
    
    # Positional factors (0-600, 100 = default)
    # Can be set globally with cc, mob, ks, pp, pw OR separately for my/opponent
    center_control: int = 100  # cc or mycc/opcc
    mobility: int = 100  # mob or mymob/opmob
    king_safety: int = 100  # ks or myks/opks
    passed_pawns: int = 100  # pp or mypp/oppp
    pawn_weakness: int = 100  # pw or mypw/oppw
    
    # Separate my/opponent positional factors (if None, use global values above)
    my_center_control: Optional[int] = None  # mycc
    my_mobility: Optional[int] = None  # mymob
    my_king_safety: Optional[int] = None  # myks
    my_passed_pawns: Optional[int] = None  # mypp
    my_pawn_weakness: Optional[int] = None  # mypw
    
    opp_center_control: Optional[int] = None  # opcc
    opp_mobility: Optional[int] = None  # opmob
    opp_king_safety: Optional[int] = None  # opks
    opp_passed_pawns: Optional[int] = None  # oppp
    opp_pawn_weakness: Optional[int] = None  # oppw
    
    # Play style parameters
    contempt: int = 0  # cfd: Contempt for draw (-500 to 500, positive = avoid draws)
    strength: int = 100  # sop: Strength of play (0-100)
    attack_defense: int = 0  # avd: Attack vs Defense (-100 to 100)
    randomness: int = 0  # rnd: Randomness (0-100)
    
    # Search parameters
    selective_search: int = 9  # sel: Selective search depth (0-16)
    max_depth: int = 999  # md: Maximum search depth (0-999)
    
    # Hash table settings (calculated from hash size in MB)
    hash_mb: int = 16  # Will be converted to tts/ttu
    
    def to_cm_parm_string(self) -> str:
        """
        Generate cm_parm initialization string for TheKing engine
        
        Returns:
            Complete initialization string with all parameters
        """
        # Start with default settings
        init_commands = ["cm_parm default"]
        
        # Material values - opponent
        init_commands.append(
            f"cm_parm opp={self.opp_pawn} opn={self.opp_knight} "
            f"opb={self.opp_bishop} opr={self.opp_rook} opq={self.opp_queen}"
        )
        
        # Material values - own
        init_commands.append(
            f"cm_parm myp={self.my_pawn} myn={self.my_knight} "
            f"myb={self.my_bishop} myr={self.my_rook} myq={self.my_queen}"
        )
        
        # Positional factors - use separate my/opp if set, otherwise global
        if self.my_center_control is not None:
            init_commands.append(
                f"cm_parm mycc={self.my_center_control} mymob={self.my_mobility or 100} "
                f"myks={self.my_king_safety or 100} mypp={self.my_passed_pawns or 100} "
                f"mypw={self.my_pawn_weakness or 100}"
            )
            init_commands.append(
                f"cm_parm opcc={self.opp_center_control or 100} opmob={self.opp_mobility or 100} "
                f"opks={self.opp_king_safety or 100} oppp={self.opp_passed_pawns or 100} "
                f"oppw={self.opp_pawn_weakness or 100}"
            )
        else:
            # Use simplified global parameters
            init_commands.append(
                f"cm_parm cc={self.center_control} mob={self.mobility} "
                f"ks={self.king_safety} pp={self.passed_pawns} pw={self.pawn_weakness}"
            )
        
        # Play style
        init_commands.append(
            f"cm_parm cfd={self.contempt} sop={self.strength} avd={self.attack_defense} "
            f"rnd={self.randomness} sel={self.selective_search} md={self.max_depth}"
        )
        
        # Hash table (convert MB to bytes for tts parameter)
        tts = self.hash_mb * 1024 * 1024
        init_commands.append(f"cm_parm tts={tts}")
        
        return "\n".join(init_commands)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'description': self.description,
            'opp_pawn': self.opp_pawn,
            'opp_knight': self.opp_knight,
            'opp_bishop': self.opp_bishop,
            'opp_rook': self.opp_rook,
            'opp_queen': self.opp_queen,
            'my_pawn': self.my_pawn,
            'my_knight': self.my_knight,
            'my_bishop': self.my_bishop,
            'my_rook': self.my_rook,
            'my_queen': self.my_queen,
            'center_control': self.center_control,
            'mobility': self.mobility,
            'king_safety': self.king_safety,
            'passed_pawns': self.passed_pawns,
            'pawn_weakness': self.pawn_weakness,
            'my_center_control': self.my_center_control,
            'my_mobility': self.my_mobility,
            'my_king_safety': self.my_king_safety,
            'my_passed_pawns': self.my_passed_pawns,
            'my_pawn_weakness': self.my_pawn_weakness,
            'opp_center_control': self.opp_center_control,
            'opp_mobility': self.opp_mobility,
            'opp_king_safety': self.opp_king_safety,
            'opp_passed_pawns': self.opp_passed_pawns,
            'opp_pawn_weakness': self.opp_pawn_weakness,
            'contempt': self.contempt,
            'strength': self.strength,
            'attack_defense': self.attack_defense,
            'randomness': self.randomness,
            'selective_search': self.selective_search,
            'max_depth': self.max_depth,
            'hash_mb': self.hash_mb
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'ChessmasterPersonality':
        """Create personality from dictionary"""
        return ChessmasterPersonality(**data)


# Predefined personalities based on famous settings
PERSONALITY_PRESETS = {
    "CM9_T05": ChessmasterPersonality(
        name="CM9_T05",
        description="Tactical and aggressive tournament setting by Kurt Utzinger & Rolf Bühler",
        # Material - slightly favor Queen
        my_queen=101,  # Slightly higher value for our queen
        # Positional emphasis
        center_control=105,  # Strong center
        mobility=110,  # High mobility
        king_safety=155,  # Very strong king safety priority
        # Play style
        strength=100,  # Full strength
        selective_search=12,  # Deep selective search
        max_depth=99,
        hash_mb=16
    ),
    
    "Default": ChessmasterPersonality(
        name="Default",
        description="Standard Chessmaster default personality",
        # All values at 100 (balanced)
        selective_search=9,
        max_depth=99,
        hash_mb=16
    ),
    
    # === LEGENDARY GRANDMASTERS - MANUAL CONFIGURATIONS ===
    
    "Kasparov_GM": ChessmasterPersonality(
        name="Kasparov (GM)",
        description="Garry Kasparov - The Beast of Baku. Dynamic, aggressive, deep preparation",
        # Material - values all pieces highly
        my_queen=105,
        my_rook=102,
        my_bishop=101,
        # Positional
        center_control=130,  # Dominant center control
        mobility=135,  # Maximum piece activity
        king_safety=110,
        passed_pawns=125,
        # Style - Ultra-aggressive but calculated
        contempt=150,  # Never accepts draws easily
        attack_defense=70,  # Heavily attack-oriented
        strength=100,
        randomness=3,  # Very consistent, but not robotic
        selective_search=15,
        max_depth=99,
        hash_mb=64
    ),
    
    "Fischer_GM": ChessmasterPersonality(
        name="Fischer (GM)",
        description="Bobby Fischer - Perfection incarnate. Crystal clear play, devastating endgames",
        # Material - Slightly favor rooks (endgame strength)
        my_rook=103,
        my_bishop=101,
        # Positional - Near perfect evaluation
        center_control=120,
        mobility=125,
        king_safety=130,  # Excellent king safety
        passed_pawns=130,  # Master of passed pawns
        pawn_weakness=90,  # Avoids weaknesses
        # Style
        contempt=100,  # Plays for win from equal positions
        attack_defense=40,  # Balanced but aggressive
        strength=100,
        randomness=0,  # Absolutely consistent
        selective_search=14,
        max_depth=99,
        hash_mb=64
    ),
    
    "Karpov_GM": ChessmasterPersonality(
        name="Karpov (GM)",
        description="Anatoly Karpov - The Python. Positional squeeze, prophylactic mastery",
        # Material - Standard
        # Positional - Emphasis on structure and prophylaxis
        center_control=130,
        mobility=110,
        king_safety=140,  # Exceptional king safety
        passed_pawns=125,
        pawn_weakness=85,  # Hates weaknesses
        # Style - Positional and patient
        contempt=-30,  # Accepts draws in equal positions
        attack_defense=-40,  # Defensive/positional
        strength=100,
        randomness=0,
        selective_search=15,  # Very deep positional understanding
        max_depth=99,
        hash_mb=64
    ),
    
    "Tal_GM": ChessmasterPersonality(
        name="Tal (GM)",
        description="Mikhail Tal - The Magician from Riga. Tactical wizard, sacrificial genius",
        # Material - Willing to sacrifice
        my_queen=98,  # Will sacrifice queen!
        my_rook=98,
        opp_king_safety=150,  # Attacks king relentlessly
        # Positional
        center_control=120,
        mobility=150,  # Maximum piece activity
        king_safety=90,  # Less concerned with own king
        # Style - Maximum aggression
        contempt=200,  # Never accepts draws
        attack_defense=90,  # Maximum attack
        strength=100,
        randomness=15,  # Unpredictable brilliancies
        selective_search=16,  # Deep tactical vision
        max_depth=99,
        hash_mb=64
    ),
    
    "Petrosian_GM": ChessmasterPersonality(
        name="Petrosian (GM)",
        description="Tigran Petrosian - Iron Tigran. Master of defense, prophylaxis perfected",
        # Material - Standard
        # Positional - Ultimate defense
        center_control=120,
        mobility=100,
        king_safety=160,  # Fortress-like king safety
        passed_pawns=110,
        pawn_weakness=80,  # Absolute structure
        # Style - Defensive genius
        contempt=-80,  # Happy with draws
        attack_defense=-70,  # Maximum defense
        strength=100,
        randomness=0,
        selective_search=14,
        max_depth=99,
        hash_mb=32
    ),
    
    "Capablanca_GM": ChessmasterPersonality(
        name="Capablanca (GM)",
        description="José Raúl Capablanca - The Chess Machine. Effortless play, endgame virtuoso",
        # Material - Endgame emphasis
        my_rook=104,
        my_knight=99,  # Slightly prefers bishops in open positions
        my_bishop=102,
        # Positional - Natural harmony
        center_control=115,
        mobility=120,
        king_safety=120,
        passed_pawns=135,  # Endgame master
        pawn_weakness=90,
        # Style - Effortless and simple
        contempt=50,
        attack_defense=10,  # Slightly aggressive but balanced
        strength=100,
        randomness=0,  # Machine-like precision
        selective_search=13,
        max_depth=99,
        hash_mb=32
    ),
    
    "Morphy_GM": ChessmasterPersonality(
        name="Morphy (GM)",
        description="Paul Morphy - The Pride and Sorrow of Chess. Romantic era tactical genius",
        # Material
        my_bishop=103,  # Loved bishops
        my_knight=102,
        # Positional - Development and attack
        center_control=125,
        mobility=140,
        king_safety=100,
        opp_king_safety=140,  # Hunts the king
        # Style - Romantic attacking chess
        contempt=120,
        attack_defense=80,
        strength=100,
        randomness=8,
        selective_search=12,
        max_depth=99,
        hash_mb=16
    ),
    
    "Alekhine_GM": ChessmasterPersonality(
        name="Alekhine (GM)",
        description="Alexander Alekhine - The Tactician. Complex combinations, deep strategy",
        # Material
        my_queen=103,
        my_knight=102,
        # Positional
        center_control=125,
        mobility=130,
        king_safety=105,
        passed_pawns=120,
        # Style - Complex and tactical
        contempt=80,
        attack_defense=50,
        strength=100,
        randomness=5,
        selective_search=15,
        max_depth=99,
        hash_mb=32
    ),
    
    "Botvinnik_GM": ChessmasterPersonality(
        name="Botvinnik (GM)",
        description="Mikhail Botvinnik - The Patriarch. Scientific approach, deep preparation",
        # Material - Balanced
        # Positional - Scientific
        center_control=125,
        mobility=115,
        king_safety=130,
        passed_pawns=120,
        pawn_weakness=85,
        # Style - Methodical
        contempt=30,
        attack_defense=0,  # Perfectly balanced
        strength=100,
        randomness=0,
        selective_search=14,
        max_depth=99,
        hash_mb=32
    ),
    
    "Kramnik_GM": ChessmasterPersonality(
        name="Kramnik (GM)",
        description="Vladimir Kramnik - The Technician. Solid, strategic, Berlin Wall specialist",
        # Material
        my_bishop=102,  # Excellent bishop play
        # Positional
        center_control=120,
        mobility=115,
        king_safety=135,
        passed_pawns=125,
        pawn_weakness=85,
        # Style - Solid and strategic
        contempt=0,  # Pragmatic about draws
        attack_defense=-20,  # Slightly defensive
        strength=100,
        randomness=0,
        selective_search=14,
        max_depth=99,
        hash_mb=64
    ),
    
    # === STYLE-BASED PERSONALITIES ===
    
    "Aggressive": ChessmasterPersonality(
        name="Aggressive",
        description="Aggressive attacking style",
        # Favor attacking pieces
        my_queen=110,
        my_rook=105,
        # Positional
        center_control=120,
        mobility=130,
        king_safety=80,  # Less concerned with own king safety
        # Style
        contempt=100,  # Avoid draws
        attack_defense=50,  # Favor attack
        randomness=10,  # Slight unpredictability
        selective_search=11,
        max_depth=99,
        hash_mb=16
    ),
    
    "Positional": ChessmasterPersonality(
        name="Positional",
        description="Strategic and positional play",
        # Value all pieces equally but emphasize position
        center_control=140,
        mobility=120,
        king_safety=130,
        passed_pawns=120,
        pawn_weakness=120,
        # Style
        contempt=-50,  # Accept draws in equal positions
        attack_defense=-30,  # Slightly defensive
        strength=100,
        selective_search=13,  # Very deep search
        max_depth=99,
        hash_mb=32
    ),
    
    "Tactical": ChessmasterPersonality(
        name="Tactical",
        description="Sharp tactical play with calculated risks",
        # Favor active pieces
        my_queen=105,
        my_bishop=102,
        my_knight=102,
        # Positional
        center_control=110,
        mobility=140,  # Maximum mobility
        king_safety=100,
        passed_pawns=120,
        # Style
        contempt=50,
        attack_defense=30,
        randomness=5,
        selective_search=14,  # Very selective for tactics
        max_depth=99,
        hash_mb=32
    ),
    
    "Solid": ChessmasterPersonality(
        name="Solid",
        description="Solid defensive play, hard to beat",
        # Standard material
        # Positional emphasis on safety
        center_control=100,
        mobility=95,
        king_safety=150,  # Maximum king safety
        pawn_weakness=80,  # Avoid pawn weaknesses
        # Style
        contempt=-100,  # Happy with draws
        attack_defense=-50,  # Defensive
        strength=100,
        randomness=0,  # Very consistent
        selective_search=10,
        max_depth=99,
        hash_mb=16
    ),
    
    "Beginner_Friendly": ChessmasterPersonality(
        name="Beginner Friendly",
        description="Weaker setting for practice",
        strength=30,  # Much weaker
        randomness=40,  # More random moves
        selective_search=5,  # Shallow search
        max_depth=20,  # Limited depth
        contempt=0,
        hash_mb=8
    )
}


class PersonalityManager:
    """Manager for Chessmaster personalities"""
    
    def __init__(self, config_file: str = "chessmaster_personalities.json"):
        self.config_file = Path(config_file)
        self.personalities: Dict[str, ChessmasterPersonality] = {}
        self.load_personalities()
    
    def load_personalities(self):
        """Load personalities from file, or use presets if file doesn't exist"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.personalities = {
                        name: ChessmasterPersonality.from_dict(p)
                        for name, p in data.items()
                    }
                print(f"Loaded {len(self.personalities)} Chessmaster personalities")
            except Exception as e:
                print(f"Error loading personalities: {e}")
                self.personalities = PERSONALITY_PRESETS.copy()
        else:
            # Use presets
            self.personalities = PERSONALITY_PRESETS.copy()
            self.save_personalities()
    
    def save_personalities(self):
        """Save personalities to file"""
        try:
            data = {name: p.to_dict() for name, p in self.personalities.items()}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving personalities: {e}")
            return False
    
    def get_personality(self, name: str) -> Optional[ChessmasterPersonality]:
        """Get personality by name"""
        return self.personalities.get(name)
    
    def add_personality(self, personality: ChessmasterPersonality):
        """Add or update a personality"""
        self.personalities[personality.name] = personality
        self.save_personalities()
    
    def delete_personality(self, name: str) -> bool:
        """Delete a personality"""
        if name in self.personalities:
            del self.personalities[name]
            self.save_personalities()
            return True
        return False
    
    def get_all_names(self) -> list:
        """Get list of all personality names"""
        return list(self.personalities.keys())

