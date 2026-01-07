"""
Import PGN Database Script
Usage: python scripts/import_pgn_database.py <pgn_file>
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pgn_database import PGNDatabaseManager


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_pgn_database.py <pgn_file> [max_games]")
        print("\nExamples:")
        print("  python scripts/import_pgn_database.py chessmaster_games.pgn")
        print("  python scripts/import_pgn_database.py chessmaster_games.pgn 10000")
        sys.exit(1)
    
    pgn_file = sys.argv[1]
    max_games = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not os.path.exists(pgn_file):
        print(f"ERROR: File not found: {pgn_file}")
        sys.exit(1)
    
    print("="*60)
    print("PGN DATABASE IMPORT")
    print("="*60)
    print(f"File: {pgn_file}")
    print(f"Max games: {max_games if max_games else 'ALL'}")
    print("="*60 + "\n")
    
    # Import
    manager = PGNDatabaseManager()
    imported = manager.import_pgn(pgn_file, max_games)
    
    print("\n" + "="*60)
    print("IMPORT COMPLETE")
    print("="*60)
    
    # Show stats
    stats = manager.get_stats()
    print(f"Total games: {stats['total_games']}")
    print(f"Total players: {stats['total_players']}")
    print(f"Total openings: {stats['total_openings']}")
    print(f"Database size: {stats['database_size_mb']:.1f} MB")
    print("="*60)
    
    # Test search
    print("\nTest search: 'Kasparov'")
    games = manager.search_by_player("Kasparov", max_results=3)
    print(f"Found {len(games)} games")
    for i, game in enumerate(games, 1):
        white = game.headers.get("White", "?")
        black = game.headers.get("Black", "?")
        result = game.headers.get("Result", "*")
        print(f"  {i}. {white} vs {black} - {result}")


if __name__ == "__main__":
    main()

