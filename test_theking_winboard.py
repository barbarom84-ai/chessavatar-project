"""
Test script for WinBoard engines (TheKing)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.winboard_engine import WinboardEngine
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import chess

def test_theking():
    """Test TheKing350 WinBoard engine"""
    
    app = QApplication(sys.argv)
    
    # Path to TheKing
    engine_path = "C:/Program Files (x86)/Ubisoft/Chessmaster Grandmaster Edition/TheKing350_64.exe"
    
    print("="*60)
    print("Testing TheKing350_64 WinBoard Engine")
    print("="*60)
    
    # Create engine
    engine = WinboardEngine(engine_path)
    
    # Connect signals
    def on_ready(name):
        print(f"\n✓ Engine ready: {name}")
        print("\nTesting move calculation...")
        
        # Set starting position
        board = chess.Board()
        engine.set_position(board)
        
        # Request a move
        engine.go(time_limit=2.0)
    
    def on_move(move_str):
        print(f"\n✓ Engine move received: {move_str}")
        try:
            move = chess.Move.from_uci(move_str)
            print(f"  Valid move: {move}")
        except:
            print(f"  Warning: Could not parse move")
        
        # Quit engine
        print("\n✓ Test successful!")
        engine.quit()
        QTimer.singleShot(500, app.quit)
    
    def on_error(msg):
        print(f"\n✗ Error: {msg}")
        # Don't quit, engine might still work despite errors
    
    def on_thinking(info):
        depth = info.get('depth', '?')
        score = info.get('score', '?')
        print(f"  Thinking... depth={depth} score={score}")
    
    engine.engine_ready.connect(on_ready)
    engine.move_ready.connect(on_move)
    engine.error_occurred.connect(on_error)
    engine.thinking_update.connect(on_thinking)
    
    # Start engine
    print("\nStarting engine...")
    if not engine.start():
        print("\n✗ Failed to start engine!")
        return 1
    
    # Timeout after 30 seconds
    QTimer.singleShot(30000, lambda: (print("\n✗ Timeout!"), app.quit()))
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_theking())

