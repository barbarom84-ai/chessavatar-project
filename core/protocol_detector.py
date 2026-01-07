"""
Engine Protocol Detection Utility
Automatically detects if an engine uses UCI or WinBoard protocol
"""
import subprocess
import time
import threading
import queue


def detect_engine_protocol(engine_path: str, timeout: float = 3.0) -> str:
    """
    Detect the protocol of a chess engine
    
    Args:
        engine_path: Path to engine executable
        timeout: Detection timeout in seconds
        
    Returns:
        "UCI", "WinBoard", or "Unknown"
    """
    
    result_queue = queue.Queue()
    
    def test_uci():
        """Test if engine responds to UCI protocol"""
        try:
            process = subprocess.Popen(
                [engine_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # Send UCI command
            process.stdin.write("uci\n")
            process.stdin.flush()
            
            # Wait for response
            start = time.time()
            while time.time() - start < timeout:
                line = process.stdout.readline().strip()
                if line:
                    print(f"UCI test: {line}")
                    if "uciok" in line.lower():
                        result_queue.put("UCI")
                        process.terminate()
                        return
                    if "unknown command" in line.lower() or "error" in line.lower():
                        break
            
            process.terminate()
            
        except Exception as e:
            print(f"UCI test error: {e}")
    
    def test_winboard():
        """Test if engine responds to WinBoard protocol"""
        try:
            process = subprocess.Popen(
                [engine_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # Send XBoard commands
            process.stdin.write("xboard\n")
            process.stdin.flush()
            time.sleep(0.2)
            
            process.stdin.write("protover 2\n")
            process.stdin.flush()
            
            # Wait for response
            start = time.time()
            while time.time() - start < timeout:
                line = process.stdout.readline().strip()
                if line:
                    print(f"WinBoard test: {line}")
                    # WinBoard engines respond with "feature" lines
                    if "feature" in line.lower():
                        result_queue.put("WinBoard")
                        process.terminate()
                        return
                    # Some old engines don't support protover 2 but still work
                    # If they don't error on xboard command, assume WinBoard
                    if time.time() - start > 1.0:
                        # Try a simple command
                        process.stdin.write("new\n")
                        process.stdin.flush()
                        time.sleep(0.3)
                        # If no error, assume WinBoard
                        result_queue.put("WinBoard")
                        process.terminate()
                        return
            
            process.terminate()
            
        except Exception as e:
            print(f"WinBoard test error: {e}")
    
    # Try UCI first (more common)
    print(f"Testing protocol for: {engine_path}")
    print("Trying UCI...")
    
    uci_thread = threading.Thread(target=test_uci, daemon=True)
    uci_thread.start()
    uci_thread.join(timeout=timeout)
    
    if not result_queue.empty():
        protocol = result_queue.get()
        print(f"OK Detected protocol: {protocol}")
        return protocol
    
    # Try WinBoard
    print("Trying WinBoard...")
    wb_thread = threading.Thread(target=test_winboard, daemon=True)
    wb_thread.start()
    wb_thread.join(timeout=timeout)
    
    if not result_queue.empty():
        protocol = result_queue.get()
        print(f"OK Detected protocol: {protocol}")
        return protocol
    
    print("X Could not detect protocol")
    return "Unknown"


if __name__ == "__main__":
    """Test protocol detection"""
    import sys
    
    engines = [
        ("Stockfish", "C:/Users/marco/Downloads/stockfish-windows-x86-64-avx2/stockfish/stockfish-windows-x86-64-avx2.exe"),
        ("TheKing350_64", "C:/Program Files (x86)/Ubisoft/Chessmaster Grandmaster Edition/TheKing350_64.exe"),
        ("TheKing350", "C:/Program Files (x86)/Ubisoft/Chessmaster Grandmaster Edition/TheKing350.exe"),
    ]
    
    for name, path in engines:
        print("\n" + "="*60)
        print(f"Testing: {name}")
        print("="*60)
        protocol = detect_engine_protocol(path)
        print(f"Result: {name} -> {protocol}\n")

