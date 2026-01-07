"""
Test SVG Piece Renderer
Quick test to verify SVG pieces render correctly
"""
from core.svg_pieces import SVGPieceRenderer
import chess


def test_svg_renderer():
    print("Testing SVG Piece Renderer...")
    print("=" * 60)
    
    renderer = SVGPieceRenderer("cburnett")
    
    # Test rendering each piece
    pieces = [
        (chess.KING, chess.WHITE, "White King"),
        (chess.QUEEN, chess.WHITE, "White Queen"),
        (chess.ROOK, chess.WHITE, "White Rook"),
        (chess.BISHOP, chess.WHITE, "White Bishop"),
        (chess.KNIGHT, chess.WHITE, "White Knight"),
        (chess.PAWN, chess.WHITE, "White Pawn"),
        (chess.KING, chess.BLACK, "Black King"),
        (chess.QUEEN, chess.BLACK, "Black Queen"),
        (chess.ROOK, chess.BLACK, "Black Rook"),
        (chess.BISHOP, chess.BLACK, "Black Bishop"),
        (chess.KNIGHT, chess.BLACK, "Black Knight"),
        (chess.PAWN, chess.BLACK, "Black Pawn"),
    ]
    
    size = 64
    success = 0
    
    for piece_type, color, name in pieces:
        pixmap = renderer.render_piece(piece_type, color, size)
        if pixmap and not pixmap.isNull():
            print(f"  [OK] {name} - Rendered at {size}x{size}")
            success += 1
        else:
            print(f"  [FAIL] {name} - Failed to render")
    
    print("=" * 60)
    print(f"Result: {success}/12 pieces rendered successfully")
    
    # Test cache
    print("\nTesting cache...")
    pixmap1 = renderer.render_piece(chess.KING, chess.WHITE, 64)
    pixmap2 = renderer.render_piece(chess.KING, chess.WHITE, 64)
    if pixmap1 == pixmap2:
        print("  [OK] Cache working (same object returned)")
    else:
        print("  [INFO] Different objects (cache may not be identity-based)")
    
    # Test different sizes
    print("\nTesting different sizes...")
    for size in [32, 64, 128]:
        pixmap = renderer.render_piece(chess.KING, chess.WHITE, size)
        if pixmap:
            print(f"  [OK] Rendered at {size}x{size}")
    
    print("\n" + "=" * 60)
    print("SVG Renderer test complete!")
    
    return success == 12


if __name__ == "__main__":
    success = test_svg_renderer()
    if success:
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[WARNING] Some tests failed")

