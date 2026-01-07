"""
Script to import Chessmaster personalities and merge them with manual GM personalities
Generates a complete personality database
"""
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.cmp_parser import CMPParser
from core.chessmaster_personalities import PERSONALITY_PRESETS, PersonalityManager


def main():
    """Main import and merge function"""
    print("=" * 70)
    print("CHESSMASTER PERSONALITY IMPORTER")
    print("=" * 70)
    
    # Initialize personality manager
    manager = PersonalityManager("chessmaster_personalities.json")
    
    # Step 1: Add all manual GM personalities first (they take priority)
    print("\n[Step 1] Loading manual GM personalities...")
    manual_count = 0
    for name, personality in PERSONALITY_PRESETS.items():
        manager.add_personality(personality)
        manual_count += 1
    print(f"  -> Added {manual_count} manual personalities")
    
    # Step 2: Import from Chessmaster installation
    print("\n[Step 2] Importing from Chessmaster installation...")
    chessmaster_path = "c:/Program Files (x86)/Ubisoft/Chessmaster Grandmaster Edition"
    
    try:
        imported = CMPParser.import_chessmaster_personalities(chessmaster_path)
        
        if imported:
            # Add imported personalities (skip if name conflicts with manual)
            added_count = 0
            skipped_count = 0
            
            for name, personality in imported.items():
                # Check if this name exists in manual presets
                if name in PERSONALITY_PRESETS:
                    # Use the manual version (GM versions take priority)
                    print(f"  -> Skipping '{name}' (manual version exists)")
                    skipped_count += 1
                    continue
                
                manager.add_personality(personality)
                added_count += 1
            
            print(f"  -> Added {added_count} Chessmaster personalities")
            print(f"  -> Skipped {skipped_count} (replaced by manual GM versions)")
        else:
            print("  -> WARNING: Could not import from Chessmaster")
            print("             Using only manual personalities")
    
    except Exception as e:
        print(f"  -> ERROR during import: {e}")
        print("  -> Continuing with manual personalities only")
    
    # Step 3: Save complete database
    print("\n[Step 3] Saving personality database...")
    manager.save_personalities()
    
    # Step 4: Summary
    print("\n" + "=" * 70)
    print("IMPORT COMPLETE")
    print("=" * 70)
    
    total = len(manager.personalities)
    print(f"\nTotal personalities in database: {total}")
    
    # Show categories
    gm_personalities = [p for p in manager.personalities.keys() if "_GM" in p or p in ["Kasparov_GM", "Fischer_GM", "Karpov_GM", "Tal_GM", "Petrosian_GM", "Capablanca_GM", "Morphy_GM", "Alekhine_GM", "Botvinnik_GM", "Kramnik_GM"]]
    cm_personalities = [p for p in manager.personalities.keys() if "From Chessmaster" in manager.personalities[p].description]
    style_personalities = [p for p in manager.personalities.keys() if p in ["Aggressive", "Positional", "Tactical", "Solid", "Beginner_Friendly", "Default", "CM9_T05"]]
    
    print(f"\nBreakdown:")
    print(f"  - Legendary Grandmasters (manual): {len(gm_personalities)}")
    print(f"  - Style-based presets: {len(style_personalities)}")
    print(f"  - Chessmaster imports: {len(cm_personalities)}")
    
    print(f"\n\nLegendary GMs available:")
    for name in sorted(gm_personalities):
        pers = manager.get_personality(name)
        if pers:
            print(f"  * {name:20s} - {pers.description}")
    
    print(f"\n\nStyle presets:")
    for name in sorted(style_personalities):
        pers = manager.get_personality(name)
        if pers:
            print(f"  * {name:20s} - {pers.description}")
    
    print(f"\n\nSample Chessmaster personalities:")
    for name in sorted(cm_personalities)[:10]:
        pers = manager.get_personality(name)
        if pers:
            print(f"  * {name}")
    
    if len(cm_personalities) > 10:
        print(f"  ... and {len(cm_personalities) - 10} more")
    
    print("\n" + "=" * 70)
    print("Personality database saved to: chessmaster_personalities.json")
    print("=" * 70)


if __name__ == "__main__":
    main()

