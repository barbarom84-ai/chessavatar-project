"""
Avatar Worker - Thread-safe worker for avatar chess engine
Similar to EngineWorker but specifically for avatar opponents
"""
import asyncio
import os
import random
from typing import Optional, Dict
from PyQt6.QtCore import QObject, QThread, pyqtSignal
import chess
import chess.engine
from core.style_analyzer import PlayerStyle


class AvatarWorker(QObject):
    """Worker for managing avatar engine in a separate thread with asyncio loop"""
    
    # Signals
    started = pyqtSignal(str)  # Emits avatar name when started
    stopped = pyqtSignal()
    error = pyqtSignal(str)  # Error message
    move_ready = pyqtSignal(object)  # Emits chess.Move when move is calculated
    
    # Internal signal for starting engine
    start_requested = pyqtSignal(str, dict, object)  # path, uci_options, player_style
    stop_requested = pyqtSignal()
    move_requested = pyqtSignal(object, float)  # board, time_limit
    
    def __init__(self):
        super().__init__()
        self.engine: Optional[chess.engine.SimpleEngine] = None
        self.transport = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.player_style: Optional[PlayerStyle] = None
        self.uci_options: Dict = {}
        self.avatar_name: str = ""
        
        # Connect internal signals
        self.start_requested.connect(self._start_engine_slot)
        self.stop_requested.connect(self._stop_engine_slot)
        self.move_requested.connect(self._get_move_slot)
        
    def run_loop(self):
        """Run permanent asyncio event loop in this thread"""
        print("DEBUG: AvatarWorker - Démarrage de l'event loop permanent")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        print("DEBUG: AvatarWorker - Event loop arrêté")
    
    def _start_engine_slot(self, engine_path: str, uci_options: dict, player_style: object):
        """Slot to start engine (called in worker thread)"""
        print(f"DEBUG: AvatarWorker - _start_engine_slot appelé avec {engine_path}")
        self.uci_options = uci_options.copy()
        self.player_style = player_style
        self.avatar_name = player_style.username if player_style else "Avatar"
        
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self.start_engine(engine_path),
                self.loop
            )
    
    def _stop_engine_slot(self):
        """Slot to stop engine (called in worker thread)"""
        print("DEBUG: AvatarWorker - _stop_engine_slot appelé")
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self.stop_engine(),
                self.loop
            )
    
    def _get_move_slot(self, board: chess.Board, time_limit: float):
        """Slot to get move (called in worker thread)"""
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self.get_best_move(board, time_limit),
                self.loop
            )
    
    async def start_engine(self, engine_path: str):
        """Start the avatar engine"""
        try:
            print(f"DEBUG: AvatarWorker.start_engine appelé avec {engine_path}")
            
            # Start UCI engine
            self.transport, self.engine = await chess.engine.popen_uci(engine_path)
            print(f"DEBUG: AvatarWorker - Moteur UCI démarré")
            
            # Apply UCI options
            # Filter out auto-managed options
            AUTO_MANAGED_OPTIONS = {"MultiPV", "Ponder"}
            
            # Get CPU count for default threads
            cpu_count = os.cpu_count() or 1
            
            # Build configuration
            config_options = {}
            
            # Skill Level (from player style)
            if "Skill Level" in self.uci_options:
                skill_level = self.uci_options["Skill Level"]
                if 0 <= skill_level <= 20:
                    config_options["Skill Level"] = skill_level
                    print(f"DEBUG: AvatarWorker - Skill Level: {skill_level}")
            
            # UCI_LimitStrength and UCI_Elo (for avatar strength)
            if "UCI_LimitStrength" in self.uci_options:
                config_options["UCI_LimitStrength"] = self.uci_options["UCI_LimitStrength"]
            
            if "UCI_Elo" in self.uci_options:
                elo = self.uci_options["UCI_Elo"]
                if 1000 <= elo <= 3000:
                    config_options["UCI_Elo"] = elo
                    print(f"DEBUG: AvatarWorker - UCI_Elo: {elo}")
            
            # Threads (default to CPU count / 2 to leave resources for UI)
            if "Threads" not in self.uci_options:
                config_options["Threads"] = max(1, cpu_count // 2)
            else:
                config_options["Threads"] = self.uci_options["Threads"]
            
            # Hash (default to 128 MB for avatar)
            if "Hash" not in self.uci_options:
                config_options["Hash"] = 128
            else:
                config_options["Hash"] = self.uci_options["Hash"]
            
            # Add other options, filtering AUTO_MANAGED_OPTIONS
            for key, value in self.uci_options.items():
                if key not in config_options and key not in AUTO_MANAGED_OPTIONS:
                    config_options[key] = value
            
            # Filter again to be safe
            config_options_filtered = {
                k: v for k, v in config_options.items() 
                if k not in AUTO_MANAGED_OPTIONS
            }
            
            print(f"DEBUG: AvatarWorker - Configuration UCI: {config_options_filtered}")
            
            # Apply configuration
            await self.engine.configure(config_options_filtered)
            
            print(f"DEBUG: AvatarWorker - Moteur configuré avec succès")
            self.started.emit(self.avatar_name)
            
        except Exception as e:
            error_msg = f"Failed to start avatar engine: {str(e)}"
            print(f"ERROR: AvatarWorker - {error_msg}")
            import traceback
            traceback.print_exc()
            self.error.emit(error_msg)
    
    async def stop_engine(self):
        """Stop the avatar engine"""
        try:
            print("DEBUG: AvatarWorker.stop_engine appelé")
            if self.engine:
                try:
                    await self.engine.quit()
                    print("DEBUG: AvatarWorker - Moteur arrêté")
                except Exception as e:
                    print(f"DEBUG: AvatarWorker - Erreur lors de l'arrêt: {e}")
                finally:
                    self.engine = None
                    self.transport = None
            self.stopped.emit()
        except Exception as e:
            print(f"ERROR: AvatarWorker.stop_engine - {e}")
    
    async def get_best_move(self, board: chess.Board, time_limit: float = 2.0):
        """
        Get best move from avatar engine
        May occasionally make suboptimal moves to simulate human play
        """
        if not self.engine:
            print("ERROR: AvatarWorker.get_best_move - Engine not running")
            self.error.emit("Engine not running")
            return
        
        try:
            print(f"DEBUG: AvatarWorker.get_best_move appelé (time_limit={time_limit}s)")
            
            # Calculate error probability based on player style
            error_probability = self._calculate_error_probability()
            
            # Calculate depth limit based on skill
            depth_limit = self._calculate_depth_limit()
            
            # Decide if we should make an "error" (play suboptimal move)
            make_error = random.random() < error_probability
            
            legal_moves_count = board.legal_moves.count()
            print(f"DEBUG: AvatarWorker - Legal moves: {legal_moves_count}, Make error: {make_error}")
            
            if make_error and legal_moves_count > 3:
                # Get top 3-5 moves and pick a random one (simulate human mistake)
                multipv = min(5, legal_moves_count)
                print(f"DEBUG: AvatarWorker - Analyse MultiPV={multipv} pour erreur humaine")
                
                with await self.engine.analysis(
                    board,
                    chess.engine.Limit(depth=depth_limit, time=time_limit),
                    multipv=multipv
                ) as analysis:
                    await analysis.wait()
                    
                    # Collect all PVs
                    pvs = []
                    # Handle both dict and list formats for multipv
                    multipv_data = analysis.multipv
                    if isinstance(multipv_data, dict):
                        multipv_items = multipv_data.values()
                    else:
                        # If it's already a list or iterable
                        multipv_items = multipv_data
                    
                    for info in multipv_items:
                        if "pv" in info and len(info["pv"]) > 0:
                            pvs.append(info["pv"][0])
                    
                    if len(pvs) > 1:
                        # Pick 2nd to 5th best move (not the best one)
                        pv_index = random.randint(1, len(pvs) - 1)
                        move = pvs[pv_index]
                        print(f"DEBUG: AvatarWorker - Coup suboptimal choisi: {move.uci()} (#{pv_index + 1})")
                        self.move_ready.emit(move)
                        return
            
            # Play best move
            print(f"DEBUG: AvatarWorker - Recherche du meilleur coup (depth={depth_limit})")
            result = await self.engine.play(
                board,
                chess.engine.Limit(depth=depth_limit, time=time_limit)
            )
            
            if result.move:
                print(f"DEBUG: AvatarWorker - Meilleur coup trouvé: {result.move.uci()}")
                self.move_ready.emit(result.move)
            else:
                print("ERROR: AvatarWorker - Aucun coup trouvé")
                self.error.emit("No move found")
            
        except Exception as e:
            error_msg = f"Error getting move: {str(e)}"
            print(f"ERROR: AvatarWorker.get_best_move - {error_msg}")
            import traceback
            traceback.print_exc()
            self.error.emit(error_msg)
    
    def _calculate_error_probability(self) -> float:
        """Calculate probability of making a suboptimal move"""
        if not self.player_style:
            return 0.10  # 10% default
        
        # Lower Elo → higher error rate
        # 1200 Elo: 30% errors
        # 1600 Elo: 15% errors
        # 2000 Elo: 5% errors
        # 2400+ Elo: 2% errors
        
        elo = self.player_style.average_elo
        
        if elo < 1200:
            return 0.30
        elif elo < 1400:
            return 0.25
        elif elo < 1600:
            return 0.15
        elif elo < 1800:
            return 0.10
        elif elo < 2000:
            return 0.05
        elif elo < 2200:
            return 0.03
        else:
            return 0.02
    
    def _calculate_depth_limit(self) -> int:
        """Calculate search depth based on skill level"""
        if not self.player_style:
            return 10  # Default depth
        
        # Map Elo to depth
        # Lower Elo → shallow depth
        # Higher Elo → deeper depth
        
        elo = self.player_style.average_elo
        
        if elo < 1200:
            return 4
        elif elo < 1400:
            return 6
        elif elo < 1600:
            return 8
        elif elo < 1800:
            return 10
        elif elo < 2000:
            return 13
        elif elo < 2200:
            return 16
        else:
            return 20


class AvatarEngineManager(QObject):
    """Manager for avatar chess engines (similar to EngineManager)"""
    
    # Signals
    avatar_started = pyqtSignal(str)  # avatar name
    avatar_stopped = pyqtSignal()
    avatar_error = pyqtSignal(str)
    move_ready = pyqtSignal(object)  # chess.Move
    
    def __init__(self):
        super().__init__()
        self.worker: Optional[AvatarWorker] = None
        self.worker_thread: Optional[QThread] = None
        self.active_avatar_id: Optional[str] = None
        self.is_running: bool = False
    
    def start_avatar(self, avatar_id: str, engine_path: str, player_style: PlayerStyle, uci_options: Optional[Dict] = None):
        """
        Start avatar engine
        
        Args:
            avatar_id: Unique avatar identifier
            engine_path: Path to Stockfish executable
            player_style: Player style for configuration
            uci_options: Optional manual UCI options override
        """
        print(f"DEBUG: AvatarEngineManager.start_avatar appelé pour {avatar_id}")
        
        # Stop any existing avatar
        if self.is_running:
            print("DEBUG: AvatarEngineManager - Arrêt de l'avatar existant")
            self.stop_avatar()
        
        # Calculate UCI options from player style
        calculated_options = self._calculate_uci_options(player_style)
        
        # Merge with manual overrides if provided
        if uci_options:
            calculated_options.update(uci_options)
        
        print(f"DEBUG: AvatarEngineManager - Options UCI finales: {calculated_options}")
        
        # Create worker and thread
        self.worker = AvatarWorker()
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker.started.connect(self._on_avatar_started)
        self.worker.stopped.connect(self._on_avatar_stopped)
        self.worker.error.connect(self._on_avatar_error)
        self.worker.move_ready.connect(self._on_move_ready)
        
        # Start thread with event loop
        self.worker_thread.started.connect(self.worker.run_loop)
        self.worker_thread.start()
        
        # Wait a bit for event loop to be ready
        from PyQt6.QtCore import QThread as QT
        QT.msleep(100)
        
        # Request engine start
        self.active_avatar_id = avatar_id
        self.worker.start_requested.emit(engine_path, calculated_options, player_style)
        
        print(f"DEBUG: AvatarEngineManager - Signal start_requested émis")
    
    def stop_avatar(self):
        """Stop the active avatar engine"""
        print("DEBUG: AvatarEngineManager.stop_avatar appelé")
        
        if not self.worker or not self.worker_thread:
            print("DEBUG: AvatarEngineManager - Pas de worker actif")
            return
        
        try:
            # Request stop
            self.worker.stop_requested.emit()
            
            # Wait for stop
            self.worker_thread.wait(2000)
            
            # Stop event loop
            if self.worker.loop:
                print("DEBUG: AvatarEngineManager - Arrêt de l'event loop")
                self.worker.loop.call_soon_threadsafe(self.worker.loop.stop)
            
            # Quit thread
            self.worker_thread.quit()
            self.worker_thread.wait(1000)
            
            # Cleanup
            self.worker = None
            self.worker_thread = None
            self.active_avatar_id = None
            self.is_running = False
            
            print("DEBUG: AvatarEngineManager - Avatar arrêté avec succès")
            
        except Exception as e:
            print(f"ERROR: AvatarEngineManager.stop_avatar - {e}")
            import traceback
            traceback.print_exc()
    
    def request_move(self, board: chess.Board, time_limit: float = 2.0):
        """Request a move from the avatar"""
        if not self.is_running or not self.worker:
            print("ERROR: AvatarEngineManager.request_move - Avatar not running")
            return
        
        print(f"DEBUG: AvatarEngineManager.request_move - Demande de coup")
        self.worker.move_requested.emit(board.copy(), time_limit)
    
    def _calculate_uci_options(self, player_style: PlayerStyle) -> Dict:
        """Calculate UCI options from player style with custom config support"""
        options = {}
        
        # Check for custom configuration
        custom_config = player_style.username  # We'll need to pass style_data differently
        # For now, use default calculation
        
        # Skill Level (0-20) based on Elo
        elo = player_style.average_elo
        
        if elo < 1200:
            skill_level = 0
        elif elo < 1400:
            skill_level = 5
        elif elo < 1600:
            skill_level = 8
        elif elo < 1800:
            skill_level = 12
        elif elo < 2000:
            skill_level = 15
        elif elo < 2200:
            skill_level = 18
        else:
            skill_level = 20
        
        options["Skill Level"] = skill_level
        options["UCI_LimitStrength"] = True
        options["UCI_Elo"] = min(3000, max(1000, elo))
        
        # Threads and Hash (conservative for avatar)
        options["Threads"] = max(1, (os.cpu_count() or 1) // 2)
        options["Hash"] = 128
        
        print(f"DEBUG: AvatarEngineManager - Options calculées: Skill={skill_level}, Elo={elo}")
        
        return options
        
        return options
    
    def _on_avatar_started(self, avatar_name: str):
        """Handle avatar started"""
        print(f"DEBUG: AvatarEngineManager - Avatar démarré: {avatar_name}")
        self.is_running = True
        self.avatar_started.emit(avatar_name)
    
    def _on_avatar_stopped(self):
        """Handle avatar stopped"""
        print("DEBUG: AvatarEngineManager - Avatar arrêté")
        self.is_running = False
        self.avatar_stopped.emit()
    
    def _on_avatar_error(self, error_msg: str):
        """Handle avatar error"""
        print(f"ERROR: AvatarEngineManager - Erreur: {error_msg}")
        self.avatar_error.emit(error_msg)
    
    def _on_move_ready(self, move: chess.Move):
        """Handle move ready"""
        print(f"DEBUG: AvatarEngineManager - Coup prêt: {move.uci()}")
        self.move_ready.emit(move)
    
    def is_avatar_running(self) -> bool:
        """Check if avatar is running"""
        return self.is_running

