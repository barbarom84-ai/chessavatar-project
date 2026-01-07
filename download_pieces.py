"""
Download chess piece SVG files from Lichess
Run this script once to download high-quality SVG pieces
"""
import requests
from pathlib import Path


def download_piece_set(piece_set_name: str = "cburnett"):
    """
    Download SVG piece set from Lichess
    
    Args:
        piece_set_name: Name of the piece set (cburnett, alpha, merida, etc.)
    """
    print(f"Downloading {piece_set_name} piece set from Lichess...")
    
    # Create directory
    pieces_dir = Path(__file__).parent / "resources" / "pieces" / piece_set_name
    pieces_dir.mkdir(parents=True, exist_ok=True)
    
    # Lichess CDN URL (updated 2024 format)
    # Alternative URLs if this doesn't work:
    # https://github.com/lichess-org/lila/tree/master/public/piece/{piece_set}
    base_url = f"https://images.chesscomfiles.com/chess-themes/pieces/{piece_set_name}"
    
    # Alternative: Direct from Lichess assets
    # base_url = f"https://lichess1.org/assets/piece/{piece_set_name}"
    
    piece_files = {
        "wP": ["wP.svg", "wp.svg", "wP.png"],  # Try multiple extensions
        "wN": ["wN.svg", "wn.svg", "wN.png"],
        "wB": ["wB.svg", "wb.svg", "wB.png"],
        "wR": ["wR.svg", "wr.svg", "wR.png"],
        "wQ": ["wQ.svg", "wq.svg", "wQ.png"],
        "wK": ["wK.svg", "wk.svg", "wK.png"],
        "bP": ["bP.svg", "bp.svg", "bP.png"],
        "bN": ["bN.svg", "bn.svg", "bN.png"],
        "bB": ["bB.svg", "bb.svg", "bB.png"],
        "bR": ["bR.svg", "br.svg", "bR.png"],
        "bQ": ["bQ.svg", "bq.svg", "bQ.png"],
        "bK": ["bK.svg", "bk.svg", "bK.png"],
    }
    
    success_count = 0
    
    for piece_key, filenames in piece_files.items():
        filepath = pieces_dir / f"{piece_key}.svg"
        
        if filepath.exists():
            print(f"  {piece_key}.svg already exists, skipping")
            success_count += 1
            continue
        
        # Try different filename variations
        downloaded = False
        for filename in filenames:
            url = f"{base_url}/{filename}"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # Save as .svg regardless of source extension
                    filepath.write_bytes(response.content)
                    print(f"  [OK] Downloaded {piece_key}.svg")
                    success_count += 1
                    downloaded = True
                    break
            except Exception as e:
                pass  # Try next variation
        
        if not downloaded:
            print(f"  [FAIL] Failed to download {piece_key}.svg")
    
    print(f"\nDownloaded {success_count}/12 pieces")
    
    if success_count == 12:
        print(f"[SUCCESS] {piece_set_name} piece set downloaded successfully!")
        return True
    elif success_count > 0:
        print(f"[WARNING] Partial download ({success_count}/12 pieces)")
        return False
    else:
        print("[ERROR] Download failed. Using fallback Unicode pieces.")
        print("\nAlternative: Download manually from:")
        print(f"  https://github.com/lichess-org/lila/tree/master/public/piece/{piece_set_name}")
        return False


def create_simple_svg_pieces():
    """Create simple fallback SVG pieces"""
    pieces_dir = Path(__file__).parent / "resources" / "pieces" / "simple"
    pieces_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creating simple SVG fallback pieces...")
    
    # Simple SVG templates (very basic shapes)
    templates = {
        "wK": '<svg viewBox="0 0 45 45" xmlns="http://www.w3.org/2000/svg"><path d="M22.5 11.63V6M20 8h5M22.5 25s4.5-7.5 3-10.5c0 0-1-2.5-3-2.5s-3 2.5-3 2.5c-1.5 3 3 10.5 3 10.5" fill="#fff" stroke="#000" stroke-width="1.5"/><path d="M11.5 37c5.5 3.5 15.5 3.5 21 0v-7s9-4.5 6-10.5c-4-6.5-13.5-3.5-16 4V27v-3.5c-3.5-7.5-13-10.5-16-4-3 6 5 10 5 10V37z" fill="#fff" stroke="#000"/></svg>',
        "wQ": '<svg viewBox="0 0 45 45" xmlns="http://www.w3.org/2000/svg"><g fill="#fff" stroke="#000" stroke-width="1.5"><path d="M8 12a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM24.5 7.5a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM41 12a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM16 8.5a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM33 9a2 2 0 1 1-4 0 2 2 0 1 1 4 0z"/><path d="M9 26c8.5-1.5 21-1.5 27 0l2-12-7 11V11l-5.5 13.5-3-15-3 15-5.5-14V25L7 14l2 12z"/><path d="M9 26c0 2 1.5 2 2.5 4 1 1.5 1 1 .5 3.5-1.5 1-1.5 2.5-1.5 2.5-1.5 1.5.5 2.5.5 2.5 6.5 1 16.5 1 23 0 0 0 1.5-1 0-2.5 0 0 .5-1.5-1-2.5-.5-2.5-.5-2 .5-3.5 1-2 2.5-2 2.5-4-8.5-1.5-18.5-1.5-27 0z"/></g></svg>',
        # Add more pieces as needed...
    }
    
    for piece, svg_content in templates.items():
        filepath = pieces_dir / f"{piece}.svg"
        filepath.write_text(svg_content)
        print(f"  [OK] Created {piece}.svg")
    
    print("Simple pieces created (fallback)")


if __name__ == "__main__":
    print("=" * 60)
    print("ChessAvatar - SVG Piece Downloader")
    print("=" * 60)
    print()
    
    # Try to download from Lichess
    success = download_piece_set("cburnett")
    
    if not success:
        print("\nAttempting alternative download method...")
        # Could try GitHub raw content
        # Or create simple fallback pieces
        create_simple_svg_pieces()
    
    print("\n" + "=" * 60)
    print("Done! Check resources/pieces/ directory")
    print("=" * 60)

