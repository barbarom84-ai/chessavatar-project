"""
Chessmaster CMP File Parser
Reads binary .CMP personality files from Chessmaster and converts them to ChessmasterPersonality objects
"""
import struct
from pathlib import Path
from typing import Optional, List, Dict
from core.chessmaster_personalities import ChessmasterPersonality


class CMPParser:
    """Parser for Chessmaster .CMP personality files"""
    
    # CMP file structure offsets (based on reverse engineering)
    OFFSET_HEADER = 0x00  # "Chessmaster 10th Edition" string
    OFFSET_VERSION = 0x20  # Version/Type (4 bytes int32)
    OFFSET_LEVEL = 0x24  # Skill level (4 bytes int32)
    OFFSET_RATING = 0x28  # Estimated rating (4 bytes int32)
    OFFSET_SELECTIVE = 0x2C  # Selective search (4 bytes int32)
    OFFSET_CONTEMPT_TYPE = 0x30  # Contempt type (4 bytes int32)
    OFFSET_SPECIAL_FLAG = 0x34  # Special flag (4 bytes int32)
    OFFSET_THINK_TIME = 0x38  # Think time in centiseconds (4 bytes int32)
    OFFSET_MAX_DEPTH = 0x3C  # Max depth (4 bytes int32)
    OFFSET_CONTEMPT = 0x40  # Contempt for draw (4 bytes int32)
    OFFSET_STRENGTH = 0x44  # Strength of play (4 bytes int32)
    OFFSET_RANDOMNESS = 0x48  # Randomness (4 bytes int32)
    OFFSET_AGGRESSION = 0x4C  # Aggression (4 bytes int32)
    OFFSET_ATTACK_DEF = 0x50  # Attack vs Defense (4 bytes int32)
    OFFSET_HASH_SIZE = 0x54  # Hash table size (4 bytes int32)
    
    # Material values offsets
    OFFSET_MY_PAWN = 0x5C
    OFFSET_MY_KNIGHT = 0x60
    OFFSET_MY_BISHOP = 0x64
    OFFSET_MY_ROOK = 0x68
    OFFSET_MY_QUEEN = 0x6C
    OFFSET_OPP_PAWN = 0x70
    OFFSET_OPP_KNIGHT = 0x74
    OFFSET_OPP_BISHOP = 0x78
    OFFSET_OPP_ROOK = 0x7C
    OFFSET_OPP_QUEEN = 0x80
    
    # Positional factors offsets
    OFFSET_MY_CENTER = 0x84
    OFFSET_OPP_CENTER = 0x88
    OFFSET_MY_MOBILITY = 0x8C
    OFFSET_OPP_MOBILITY = 0x90
    OFFSET_MY_KING_SAFETY = 0x94
    OFFSET_OPP_KING_SAFETY = 0x98
    OFFSET_MY_PASSED_PAWNS = 0x9C
    OFFSET_OPP_PASSED_PAWNS = 0xA0
    OFFSET_MY_PAWN_WEAKNESS = 0xA4
    OFFSET_OPP_PAWN_WEAKNESS = 0xA8
    
    # Opening book name offset
    OFFSET_OPENING_BOOK = 0xC0  # Null-terminated string
    
    def __init__(self):
        pass
    
    @staticmethod
    def parse_file(file_path: Path) -> Optional[ChessmasterPersonality]:
        """
        Parse a .CMP file and return a ChessmasterPersonality
        
        Args:
            file_path: Path to .CMP file
            
        Returns:
            ChessmasterPersonality object or None if parsing fails
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Verify it's a Chessmaster file
            header = data[0:28].decode('ascii', errors='ignore')
            if 'Chessmaster' not in header:
                print(f"Warning: {file_path.name} doesn't appear to be a Chessmaster file")
                return None
            
            # Extract personality name from filename
            name = file_path.stem
            
            # Read all parameters using struct.unpack
            def read_int32(offset):
                """Read 4-byte little-endian signed integer"""
                if offset + 4 <= len(data):
                    return struct.unpack('<i', data[offset:offset+4])[0]
                return 0
            
            # Read opening book name
            opening_book = ""
            try:
                book_start = CMPParser.OFFSET_OPENING_BOOK
                book_end = data.find(b'\x00', book_start)
                if book_end > book_start:
                    opening_book = data[book_start:book_end].decode('ascii', errors='ignore')
            except:
                pass
            
            # Create description
            description = f"From Chessmaster (Book: {opening_book})" if opening_book else "From Chessmaster"
            
            # Read material values (convert to 0-200 scale where 100 = normal)
            # CMP uses absolute values, we need to normalize them
            my_pawn = read_int32(CMPParser.OFFSET_MY_PAWN)
            my_knight = read_int32(CMPParser.OFFSET_MY_KNIGHT)
            my_bishop = read_int32(CMPParser.OFFSET_MY_BISHOP)
            my_rook = read_int32(CMPParser.OFFSET_MY_ROOK)
            my_queen = read_int32(CMPParser.OFFSET_MY_QUEEN)
            
            opp_pawn = read_int32(CMPParser.OFFSET_OPP_PAWN)
            opp_knight = read_int32(CMPParser.OFFSET_OPP_KNIGHT)
            opp_bishop = read_int32(CMPParser.OFFSET_OPP_BISHOP)
            opp_rook = read_int32(CMPParser.OFFSET_OPP_ROOK)
            opp_queen = read_int32(CMPParser.OFFSET_OPP_QUEEN)
            
            # Positional factors (already in 0-200 scale typically)
            my_center = read_int32(CMPParser.OFFSET_MY_CENTER)
            opp_center = read_int32(CMPParser.OFFSET_OPP_CENTER)
            my_mobility = read_int32(CMPParser.OFFSET_MY_MOBILITY)
            opp_mobility = read_int32(CMPParser.OFFSET_OPP_MOBILITY)
            my_king_safety = read_int32(CMPParser.OFFSET_MY_KING_SAFETY)
            opp_king_safety = read_int32(CMPParser.OFFSET_OPP_KING_SAFETY)
            my_passed_pawns = read_int32(CMPParser.OFFSET_MY_PASSED_PAWNS)
            opp_passed_pawns = read_int32(CMPParser.OFFSET_OPP_PASSED_PAWNS)
            my_pawn_weakness = read_int32(CMPParser.OFFSET_MY_PAWN_WEAKNESS)
            opp_pawn_weakness = read_int32(CMPParser.OFFSET_OPP_PAWN_WEAKNESS)
            
            # Play style parameters
            contempt = read_int32(CMPParser.OFFSET_CONTEMPT)
            strength = read_int32(CMPParser.OFFSET_STRENGTH)
            attack_def = read_int32(CMPParser.OFFSET_ATTACK_DEF)
            randomness = read_int32(CMPParser.OFFSET_RANDOMNESS)
            
            # Search parameters
            selective = read_int32(CMPParser.OFFSET_SELECTIVE)
            max_depth = read_int32(CMPParser.OFFSET_MAX_DEPTH)
            
            # Hash size (convert to MB)
            hash_size = read_int32(CMPParser.OFFSET_HASH_SIZE)
            hash_mb = max(8, min(256, hash_size // (1024 * 1024))) if hash_size > 0 else 16
            
            # Clamp values to reasonable ranges
            strength = max(0, min(100, strength))
            selective = max(0, min(16, selective))
            max_depth = max(1, min(999, max_depth))
            contempt = max(-500, min(500, contempt))
            attack_def = max(-100, min(100, attack_def))
            randomness = max(0, min(100, randomness))
            
            # Create personality
            personality = ChessmasterPersonality(
                name=name,
                description=description,
                # Material values
                my_pawn=my_pawn,
                my_knight=my_knight,
                my_bishop=my_bishop,
                my_rook=my_rook,
                my_queen=my_queen,
                opp_pawn=opp_pawn,
                opp_knight=opp_knight,
                opp_bishop=opp_bishop,
                opp_rook=opp_rook,
                opp_queen=opp_queen,
                # Positional factors - use separate my/opp values
                my_center_control=my_center,
                my_mobility=my_mobility,
                my_king_safety=my_king_safety,
                my_passed_pawns=my_passed_pawns,
                my_pawn_weakness=my_pawn_weakness,
                opp_center_control=opp_center,
                opp_mobility=opp_mobility,
                opp_king_safety=opp_king_safety,
                opp_passed_pawns=opp_passed_pawns,
                opp_pawn_weakness=opp_pawn_weakness,
                # Play style
                contempt=contempt,
                strength=strength,
                attack_defense=attack_def,
                randomness=randomness,
                # Search
                selective_search=selective,
                max_depth=max_depth,
                hash_mb=hash_mb
            )
            
            return personality
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    @staticmethod
    def parse_directory(directory_path: Path) -> Dict[str, ChessmasterPersonality]:
        """
        Parse all .CMP files in a directory
        
        Args:
            directory_path: Path to directory containing .CMP files
            
        Returns:
            Dictionary mapping personality name to ChessmasterPersonality
        """
        personalities = {}
        
        if not directory_path.exists():
            print(f"Directory not found: {directory_path}")
            return personalities
        
        cmp_files = list(directory_path.glob("*.CMP"))
        print(f"Found {len(cmp_files)} CMP files in {directory_path}")
        
        success_count = 0
        for cmp_file in cmp_files:
            personality = CMPParser.parse_file(cmp_file)
            if personality:
                personalities[personality.name] = personality
                success_count += 1
        
        print(f"Successfully parsed {success_count}/{len(cmp_files)} personalities")
        return personalities
    
    @staticmethod
    def import_chessmaster_personalities(
        chessmaster_path: str = "c:/Program Files (x86)/Ubisoft/Chessmaster Grandmaster Edition"
    ) -> Dict[str, ChessmasterPersonality]:
        """
        Import all personalities from Chessmaster installation
        
        Args:
            chessmaster_path: Path to Chessmaster installation
            
        Returns:
            Dictionary of personalities
        """
        from pathlib import Path
        
        # Find the Personnalités folder (with proper encoding)
        base_path = Path(chessmaster_path) / "Data"
        
        if not base_path.exists():
            print(f"Chessmaster Data folder not found: {base_path}")
            return {}
        
        # Find folder with "Person" in name (handles encoding issues)
        personalities_folder = None
        for folder in base_path.iterdir():
            if folder.is_dir() and "person" in folder.name.lower():
                personalities_folder = folder
                break
        
        if not personalities_folder:
            print("Could not find Chessmaster personalities folder")
            return {}
        
        print(f"Importing from: {personalities_folder}")
        return CMPParser.parse_directory(personalities_folder)


# Example usage and testing
if __name__ == "__main__":
    # Test the parser
    parser = CMPParser()
    
    # Try to import from Chessmaster installation
    personalities = CMPParser.import_chessmaster_personalities()
    
    if personalities:
        print(f"\n[OK] Successfully imported {len(personalities)} personalities!")
        print("\nSample personalities:")
        for i, (name, pers) in enumerate(list(personalities.items())[:5]):
            print(f"\n{i+1}. {name}")
            print(f"   Description: {pers.description}")
            print(f"   Strength: {pers.strength}, Contempt: {pers.contempt}")
            print(f"   Attack/Defense: {pers.attack_defense}, Randomness: {pers.randomness}")
    else:
        print("[ERROR] No personalities imported. Check Chessmaster installation path.")

