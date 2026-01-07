"""
WinBoard/XBoard Protocol Engine Manager
Handles communication with WinBoard-compatible engines like TheKing350
"""
import subprocess
import threading
import queue
import time
import chess
from typing import Optional, Callable, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal
from core.chessmaster_personalities import ChessmasterPersonality


class WinboardEngine(QObject):
    """Asynchronous WinBoard/XBoard engine implementation"""
    
    # Signals
    move_ready = pyqtSignal(str)  # Emits best move (e.g., "e2e4")
    thinking_update = pyqtSignal(dict)  # Emits thinking info (depth, score, etc.)
    error_occurred = pyqtSignal(str)  # Emits error message
    engine_ready = pyqtSignal(str)  # Emits engine name when ready
    
    def __init__(self, engine_path: str, options: Dict[str, Any] = None, personality: Optional[ChessmasterPersonality] = None):
        """
        Initialize WinBoard engine
        
        Args:
            engine_path: Path to engine executable
            options: Engine-specific options
            personality: Chessmaster personality configuration (for TheKing)
        """
        super().__init__()
        self.engine_path = engine_path
        self.options = options or {}
        self.personality = personality
        self.process: Optional[subprocess.Popen] = None
        self.output_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.is_thinking = False
        self.board = chess.Board()
        self._stop_thinking = False
        
    def start(self) -> bool:
        """
        Start the WinBoard engine
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"DEBUG: Starting WinBoard engine: {self.engine_path}")
            
            # Start engine process
            self.process = subprocess.Popen(
                [self.engine_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            self.is_running = True
            
            # Start output reading thread
            self.output_thread = threading.Thread(target=self._read_output, daemon=True)
            self.output_thread.start()
            
            # Send initialization commands
            print("DEBUG: Sending WinBoard initialization commands")
            self._send_command("xboard")
            time.sleep(0.2)
            
            # Try protover 2 (newer engines)
            self._send_command("protover 2")
            time.sleep(0.3)
            
            # If engine doesn't support protover 2, it will ignore it
            # Send basic initialization commands that work with older engines
            self._send_command("new")
            time.sleep(0.1)
            self._send_command("random")  # Enable randomness
            time.sleep(0.1)
            
            # Force mode (engine should always be ready to think)
            self._send_command("force")
            time.sleep(0.1)
            
            # Apply Chessmaster personality if provided (for TheKing)
            if self.personality:
                print(f"DEBUG: Applying Chessmaster personality: {self.personality.name}")
                self._apply_personality()
            
            # Apply engine-specific options if available
            self._apply_options()
            
            print("DEBUG: WinBoard engine initialized successfully")
            
            # Extract engine name from path
            import os
            engine_name = os.path.basename(self.engine_path).replace('.exe', '')
            self.engine_ready.emit(f"{engine_name}")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to start WinBoard engine: {e}"
            print(f"DEBUG: {error_msg}")
            self.error_occurred.emit(error_msg)
            return False
    
    def _apply_personality(self):
        """Apply Chessmaster personality configuration to TheKing engine"""
        if not self.personality:
            return
        
        # Get the cm_parm initialization string
        cm_parm_commands = self.personality.to_cm_parm_string()
        
        # Send each command line by line
        for cmd in cm_parm_commands.split('\n'):
            if cmd.strip():
                self._send_command(cmd.strip())
                time.sleep(0.05)  # Small delay between commands
        
        print(f"DEBUG: Applied personality '{self.personality.name}'")
    
    def update_personality(self, personality: ChessmasterPersonality):
        """
        Update personality on the fly
        
        Args:
            personality: New personality configuration
        """
        self.personality = personality
        if self.is_running:
            print(f"DEBUG: Updating to personality: {personality.name}")
            # Enter force mode to avoid engine thinking during update
            self._send_command("force")
            time.sleep(0.05)
            self._apply_personality()
    
    def _apply_options(self):
        """Apply engine-specific options"""
        # TheKing-specific options (legacy, prefer using personality)
        if "contempt" in self.options:
            self._send_command(f"option Contempt={self.options['contempt']}")
        
        if "style" in self.options:
            self._send_command(f"option Style={self.options['style']}")
        
        # Standard time controls
        if "time" in self.options and "otim" in self.options:
            self._send_command(f"time {self.options['time']}")
            self._send_command(f"otim {self.options['otim']}")
    
    def _send_command(self, command: str):
        """Send command to engine"""
        if self.process and self.process.stdin:
            try:
                print(f"DEBUG: >> {command}")
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
            except Exception as e:
                print(f"DEBUG: Error sending command '{command}': {e}")
                self.error_occurred.emit(f"Communication error: {e}")
    
    def _read_output(self):
        """Read engine output in separate thread"""
        if not self.process or not self.process.stdout:
            return
        
        print("DEBUG: Output reading thread started")
        
        try:
            for line in self.process.stdout:
                if not self.is_running:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                print(f"DEBUG: << {line}")
                self._parse_output(line)
                
        except Exception as e:
            print(f"DEBUG: Error reading output: {e}")
            if self.is_running:
                self.error_occurred.emit(f"Output reading error: {e}")
    
    def _parse_output(self, line: str):
        """Parse engine output"""
        # Ignore common error messages that don't affect functionality
        if "Error (unknown command): protover" in line:
            print(f"DEBUG: Engine doesn't support protover 2 (old WinBoard engine) - continuing anyway")
            return
        
        # Move output (format: "move e2e4" or just "e2e4")
        if line.startswith("move "):
            move_str = line.split()[1]
            self.is_thinking = False
            print(f"DEBUG: Engine move received: {move_str}")
            self.move_ready.emit(move_str)
            
        elif " " not in line and len(line) in [4, 5]:  # Looks like a move (e2e4 or e7e8q)
            # Some engines don't prefix with "move"
            if self.is_thinking:
                self.is_thinking = False
                print(f"DEBUG: Engine move received (no prefix): {line}")
                self.move_ready.emit(line)
        
        # Thinking output (format varies, but often contains ply/depth and score)
        # Example: "9 123 456789 12345 e2e4 e7e5 g1f3"
        # Format: ply score time nodes pv...
        elif self.is_thinking and line.split()[0].isdigit():
            parts = line.split()
            if len(parts) >= 4:
                try:
                    thinking_info = {
                        "depth": int(parts[0]),
                        "score": int(parts[1]),  # In centipawns
                        "time": float(parts[2]) / 100.0,  # Convert to seconds
                        "nodes": int(parts[3]),
                        "pv": parts[4:] if len(parts) > 4 else []
                    }
                    self.thinking_update.emit(thinking_info)
                except (ValueError, IndexError):
                    pass  # Ignore malformed thinking lines
        
        # Feature declarations (protover 2 response)
        elif line.startswith("feature"):
            # Parse features if needed
            print(f"DEBUG: Feature declaration: {line}")
            pass
        
        # Error messages (except protover which we ignore)
        elif line.startswith("Error") or line.startswith("Illegal"):
            if "protover" not in line.lower():
                print(f"DEBUG: Engine error: {line}")
                self.error_occurred.emit(line)
    
    def set_position(self, board: chess.Board):
        """
        Set current board position
        
        Args:
            board: Chess board position
        """
        self.board = board.copy()
        
        # For WinBoard, enter force mode, then send moves
        self._send_command("force")
        time.sleep(0.05)
        
        # Reset to starting position
        self._send_command("new")
        time.sleep(0.05)
        
        # Send each move in the game
        # Note: Some old WinBoard engines (like TheKing) don't support 'usermove'
        # Send moves directly in coordinate notation
        for move in board.move_stack:
            move_str = move.uci()
            self._send_command(move_str)  # Just send the move without 'usermove' prefix
            time.sleep(0.02)  # Small delay between moves
    
    def go(self, time_limit: float = 5.0):
        """
        Start engine thinking
        
        Args:
            time_limit: Time limit in seconds
        """
        if not self.is_running:
            self.error_occurred.emit("Engine not running")
            return
        
        print(f"DEBUG: Requesting engine to think (time={time_limit}s)")
        self.is_thinking = True
        self._stop_thinking = False
        
        # Exit force mode and tell engine to move
        # Set time control first (in seconds for 'st' command)
        self._send_command(f"st {time_limit}")
        time.sleep(0.05)
        
        # Tell engine it's their turn to move
        self._send_command("go")
        print("DEBUG: Sent 'go' command to WinBoard engine")
    
    def stop(self):
        """Stop engine thinking"""
        if self.is_thinking:
            print("DEBUG: Stopping engine thinking")
            self._send_command("?")  # Force move now
            self._stop_thinking = True
            self.is_thinking = False
    
    def make_move(self, move: chess.Move):
        """
        Send opponent's move to engine
        
        Args:
            move: Chess move
        """
        if not self.is_running:
            return
        
        move_str = move.uci()
        print(f"DEBUG: Sending user move: {move_str}")
        # TheKing and other old WinBoard engines don't support 'usermove'
        # Just send the move in coordinate notation directly
        self._send_command(move_str)
        self.board.push(move)
    
    def quit(self):
        """Shutdown engine"""
        print("DEBUG: Shutting down WinBoard engine")
        self.is_running = False
        self.is_thinking = False
        
        if self.process:
            try:
                self._send_command("quit")
                self.process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                print("DEBUG: Force killing engine process")
                self.process.kill()
            except Exception as e:
                print(f"DEBUG: Error during shutdown: {e}")
            
            self.process = None
        
        if self.output_thread and self.output_thread.is_alive():
            self.output_thread.join(timeout=1.0)
    
    def is_alive(self) -> bool:
        """Check if engine process is alive"""
        return self.process is not None and self.process.poll() is None
    
    def __del__(self):
        """Cleanup on deletion"""
        self.quit()

