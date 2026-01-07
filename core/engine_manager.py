"""
Engine Manager for UCI and WinBoard chess engines
Handles asynchronous communication with chess engines
"""
import asyncio
import chess
import chess.engine
import os
from typing import Optional, Dict, List, Callable
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from core.winboard_engine import WinboardEngine


class EngineInfo:
    """Information about a chess engine"""
    
    def __init__(self, name: str, path: str, protocol: str = "UCI"):
        self.name = name
        self.path = path
        self.protocol = protocol  # "UCI" or "WinBoard"
        self.options: Dict[str, any] = {}
        
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "path": self.path,
            "protocol": self.protocol,
            "options": self.options
        }
        
    @staticmethod
    def from_dict(data: dict) -> 'EngineInfo':
        """Create from dictionary"""
        engine = EngineInfo(data["name"], data["path"], data.get("protocol", "UCI"))
        engine.options = data.get("options", {})
        return engine


class EngineWorker(QObject):
    """Worker thread for engine analysis"""
    
    # Signals
    analysis_update = pyqtSignal(dict)  # Emits analysis info
    engine_ready = pyqtSignal(str)  # Engine name when ready
    engine_error = pyqtSignal(str)  # Error message
    start_requested = pyqtSignal(str, dict)  # Engine path and options (includes protocol) to start
    
    def __init__(self):
        super().__init__()
        self.engine: Optional[chess.engine.SimpleEngine] = None
        self.winboard_engine: Optional[WinboardEngine] = None  # For WinBoard engines
        self.transport = None
        self.protocol = None
        self.is_analyzing = False
        self.current_board: Optional[chess.Board] = None
        self._stop_flag = False
        self.loop = None
        self.uci_options: Dict[str, any] = {}  # Store UCI options
        self.engine_path_to_start = None  # Store engine path for deferred start
        
        # Connect start signal to slot
        self.start_requested.connect(self._start_engine_slot)
    
    def run_loop(self):
        """Run event loop continuously in worker thread"""
        print("DEBUG: Démarrage de l'event loop permanent")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()  # Loop tourne en permanence
        print("DEBUG: Event loop arrêté")
        
    def _start_engine_slot(self, engine_path: str, options: dict):
        """Slot to start engine (called via signal from main thread)"""
        # Extract protocol from options (default to UCI if not present)
        protocol = options.get("__protocol__", "UCI")
        print(f"DEBUG: _start_engine_slot appelé avec {engine_path}, protocol={protocol}")
        # Remove protocol from options before storing
        self.uci_options = {k: v for k, v in options.items() if k != "__protocol__"}
        print(f"DEBUG: Options UCI: {self.uci_options}")
        self.engine_path_to_start = engine_path
        self.protocol = protocol
        
        # Schedule engine start in the event loop
        if self.loop and self.loop.is_running():
            print("DEBUG: Planification du démarrage du moteur dans l'event loop")
            asyncio.run_coroutine_threadsafe(self.start_engine(engine_path, protocol), self.loop)
        else:
            print("DEBUG: ERREUR - Event loop n'est pas en cours d'exécution")
            self.engine_error.emit("Event loop not running")
    
    async def start_engine(self, engine_path: str, protocol: str = "UCI"):
        """Start the chess engine"""
        print(f"DEBUG: EngineWorker.start_engine appelé avec {engine_path}, protocol={protocol}")
        try:
            # Start engine with the appropriate protocol
            if protocol == "WinBoard" or protocol == "XBoard":
                print("DEBUG: Démarrage moteur WinBoard avec subprocess")
                # Use our custom WinBoard implementation
                self.winboard_engine = WinboardEngine(engine_path, self.uci_options)
                
                # Connect signals
                self.winboard_engine.engine_ready.connect(
                    lambda name: self.engine_ready.emit(f"{name} (WinBoard)")
                )
                self.winboard_engine.error_occurred.connect(
                    lambda msg: self.engine_error.emit(msg)
                )
                
                # Start engine
                if self.winboard_engine.start():
                    print("DEBUG: Moteur WinBoard démarré avec succès")
                    self.protocol = "XBoard"
                    # Note: engine_ready signal will be emitted by WinboardEngine
                else:
                    raise Exception("Failed to start WinBoard engine")
                    
            else:
                print("DEBUG: Appel de chess.engine.popen_uci")
                self.transport, self.engine = await chess.engine.popen_uci(engine_path)
                print("DEBUG: Moteur UCI démarré avec succès")
                self.protocol = "UCI"
            
                # Options automatically managed by the engine during analysis
                AUTO_MANAGED_OPTIONS = {"MultiPV", "Ponder"}
                
                # Get engine info
                engine_name = self.engine.id.get("name", "Unknown Engine")
                print(f"DEBUG: Nom du moteur: {engine_name}")
                
                # Configure UCI engine options
                # Apply default options if not provided
                config_options = {}
                cpu_count = os.cpu_count() or 1
                
                # Threads: use all CPU cores if not specified
                if "Threads" not in self.uci_options:
                    config_options["Threads"] = cpu_count
                    print(f"DEBUG: Configuration automatique - Threads: {cpu_count}")
                else:
                    config_options["Threads"] = self.uci_options["Threads"]
                    print(f"DEBUG: Configuration utilisateur - Threads: {self.uci_options['Threads']}")
                
                # Hash: 256 MB default if not specified
                if "Hash" not in self.uci_options:
                    config_options["Hash"] = 256
                    print(f"DEBUG: Configuration automatique - Hash: 256 MB")
                else:
                    config_options["Hash"] = self.uci_options["Hash"]
                    print(f"DEBUG: Configuration utilisateur - Hash: {self.uci_options['Hash']} MB")
                
                # Skill Level: apply only if >= 0 (-1 means disabled/max strength)
                if "Skill Level" in self.uci_options:
                    skill_level = self.uci_options["Skill Level"]
                    if skill_level >= 0:
                        config_options["Skill Level"] = skill_level
                        print(f"DEBUG: Configuration utilisateur - Skill Level: {skill_level}")
                    else:
                        print(f"DEBUG: Skill Level désactivé (force maximale)")
                
                # Apply any other user-specified options (except auto-managed ones)
                for key, value in self.uci_options.items():
                    if key not in config_options and key not in AUTO_MANAGED_OPTIONS:
                        config_options[key] = value
                
                # Configure the engine (filter out automatically managed options)
                print(f"DEBUG: Application de la configuration UCI: {config_options}")
                config_options_filtered = {
                    k: v for k, v in config_options.items() 
                    if k not in AUTO_MANAGED_OPTIONS
                }
                if len(config_options_filtered) < len(config_options):
                    filtered_out = [k for k in config_options if k in AUTO_MANAGED_OPTIONS]
                    print(f"DEBUG: Options auto-gérées filtrées: {', '.join(filtered_out)}")
                print(f"DEBUG: Configuration finale: {config_options_filtered}")
                
                await self.engine.configure(config_options_filtered)
                print("DEBUG: Configuration UCI appliquée avec succès")
                
                # Store the applied options (auto-managed options are kept in uci_options but not applied)
                self.uci_options = config_options_filtered.copy()
                # Note: MultiPV and Ponder are managed automatically during analysis/play
                
                print("DEBUG: Émission du signal engine_ready")
                self.engine_ready.emit(engine_name)
            
        except Exception as e:
            print(f"DEBUG: Exception dans start_engine: {e}")
            import traceback
            traceback.print_exc()
            self.engine_error.emit(f"Failed to start engine: {str(e)}")
            
    async def stop_engine(self):
        """Stop the chess engine"""
        self._stop_flag = True
        
        # Stop WinBoard engine
        if self.winboard_engine:
            try:
                self.winboard_engine.quit()
            except:
                pass
            self.winboard_engine = None
        
        # Stop UCI engine
        if self.engine:
            try:
                await self.engine.quit()
            except:
                pass
            self.engine = None
            
    async def update_option(self, name: str, value: any):
        """Update a UCI option on the fly"""
        if self.engine:
            try:
                print(f"DEBUG: Mise à jour de l'option {name} -> {value}")
                self.uci_options[name] = value
                await self.engine.configure({name: value})
            except Exception as e:
                print(f"DEBUG: Error updating option {name}: {e}")
            
    async def analyze_position(self, board: chess.Board, multipv: int = 3, time_limit: float = 1.0):
        """
        Analyze a chess position
        
        Args:
            board: Chess board position
            multipv: Number of principal variations to analyze
            time_limit: Time limit for analysis in seconds
        """
        print(f"DEBUG: EngineWorker.analyze_position appelé")
        self._stop_flag = False  # Reset stop flag for new analysis
        
        # Handle WinBoard engine - limited analysis support
        if self.winboard_engine and self.protocol == "XBoard":
            print(f"DEBUG: Analyse WinBoard - obtention du meilleur coup")
            # WinBoard doesn't have a proper analysis mode like UCI
            # We'll just get the best move and emit it as analysis data
            move = await self.get_best_move(board, time_limit)
            
            if move:
                # Emit basic analysis data
                analysis_data = {
                    "score": None,  # WinBoard doesn't provide score easily
                    "mate": None,
                    "depth": 0,
                    "nodes": 0,
                    "nps": 0,
                    "time": time_limit,
                    "pv": [board.san(move)],  # Only one move in PV
                    "multipv": 1  # WinBoard doesn't support MultiPV
                }
                self.analysis_update.emit(analysis_data)
                print(f"DEBUG: Analyse WinBoard émise: {analysis_data}")
            
            self.is_analyzing = False
            return
        
        # Handle UCI engine
        if not self.engine:
            print(f"DEBUG: Engine={self.engine}")
            return
        
        print(f"DEBUG: Configuration de l'analyse")
        self.current_board = board
        self.is_analyzing = True
        
        try:
            # Start analysis with MultiPV parameter (don't configure it - it's automatically managed)
            print(f"DEBUG: Démarrage de l'analyse avec multipv={multipv}, time_limit={time_limit}")
            with await self.engine.analysis(board, chess.engine.Limit(time=time_limit), multipv=multipv) as analysis:
                print("DEBUG: Analyse démarrée, lecture des infos...")
                async for info in analysis:
                    if self._stop_flag:
                        print("DEBUG: Analyse arrêtée (stop_flag)")
                        break
                    
                    print(f"DEBUG: Info reçue: depth={info.get('depth', 0)}")
                    
                    # Extract analysis information
                    analysis_data = {
                        "score": None,
                        "mate": None,
                        "depth": info.get("depth", 0),
                        "nodes": info.get("nodes", 0),
                        "nps": info.get("nps", 0),
                        "time": info.get("time", 0),
                        "pv": [],
                        "multipv": info.get("multipv", 1)
                    }
                    
                    # Get score
                    if "score" in info:
                        score = info["score"]
                        # Get score from white's perspective (always)
                        if score.is_mate():
                            # Mate score from white's perspective
                            analysis_data["mate"] = score.white().mate()
                        else:
                            # Centipawn score from white's perspective
                            analysis_data["score"] = score.white().score()
                            
                    # Get principal variation
                    if "pv" in info:
                        pv_moves = []
                        temp_board = board.copy()
                        for move in info["pv"][:10]:  # Limit to 10 moves
                            try:
                                san_move = temp_board.san(move)
                                pv_moves.append(san_move)
                                temp_board.push(move)
                            except:
                                break
                        analysis_data["pv"] = pv_moves
                        
                    # Emit update
                    self.analysis_update.emit(analysis_data)
                    
        except Exception as e:
            self.engine_error.emit(f"Analysis error: {str(e)}")
        finally:
            self.is_analyzing = False
    
    async def get_best_move(self, board: chess.Board, time_limit: float = 2.0):
        """
        Get best move from engine
        
        Args:
            board: Chess board position
            time_limit: Time limit for search in seconds
            
        Returns:
            Best move or None if error
        """
        print(f"DEBUG: EngineWorker.get_best_move appelé")
        self._stop_flag = False  # Reset stop flag for new move calculation
        
        # Handle WinBoard engine
        if self.winboard_engine and self.protocol == "XBoard":
            print(f"DEBUG: Demande du meilleur coup (WinBoard) avec time_limit={time_limit}")
            
            # Use a simple container to store the move (thread-safe for single write)
            move_result = {'move': None, 'received': False}
            
            def on_move_ready(move_str):
                """Callback when WinBoard engine returns a move"""
                print(f"DEBUG: WinBoard move_ready callback - move_str='{move_str}'")
                try:
                    # Convert UCI move string to chess.Move
                    move = chess.Move.from_uci(move_str)
                    print(f"DEBUG: Converted to chess.Move: {move}")
                    move_result['move'] = move
                    move_result['received'] = True
                except Exception as e:
                    print(f"DEBUG: Error parsing WinBoard move '{move_str}': {e}")
                    move_result['move'] = None
                    move_result['received'] = True
            
            # Connect signal
            self.winboard_engine.move_ready.connect(on_move_ready)
            
            try:
                # Set position and request move
                print(f"DEBUG: Setting WinBoard position and starting search")
                self.winboard_engine.set_position(board)
                self.winboard_engine.go(time_limit)
                
                # Wait for move with polling (simpler than async queue)
                start_time = asyncio.get_event_loop().time()
                timeout = time_limit + 10.0
                
                while not move_result['received']:
                    await asyncio.sleep(0.1)  # Check every 100ms
                    if asyncio.get_event_loop().time() - start_time > timeout:
                        print(f"DEBUG: Timeout waiting for WinBoard move ({timeout}s)")
                        return None
                
                move = move_result['move']
                print(f"DEBUG: Meilleur coup reçu (WinBoard): {move}")
                return move
                
            except Exception as e:
                print(f"DEBUG: Error in WinBoard get_best_move: {e}")
                import traceback
                traceback.print_exc()
                return None
            finally:
                # Disconnect signal
                try:
                    self.winboard_engine.move_ready.disconnect(on_move_ready)
                except:
                    pass
        
        # Handle UCI engine
        if not self.engine:
            print(f"DEBUG: Engine={self.engine}")
            return None
        
        try:
            print(f"DEBUG: Demande du meilleur coup (UCI) avec time_limit={time_limit}")
            result = await self.engine.play(board, chess.engine.Limit(time=time_limit))
            print(f"DEBUG: Meilleur coup reçu (UCI): {result.move}")
            return result.move
        except Exception as e:
            print(f"ERROR: get_best_move failed: {e}")
            import traceback
            traceback.print_exc()
            self.engine_error.emit(f"Best move error: {str(e)}")
            return None


class EngineManager(QObject):
    """Manager for chess engines with asynchronous communication"""
    
    # Signals
    analysis_updated = pyqtSignal(dict)
    engine_started = pyqtSignal(str)
    engine_stopped = pyqtSignal()
    engine_error = pyqtSignal(str)
    move_ready = pyqtSignal(object)  # Emits chess.Move
    
    def __init__(self):
        super().__init__()
        self.engines: List[EngineInfo] = []
        self.active_engine: Optional[EngineInfo] = None
        self.worker: Optional[EngineWorker] = None
        self.worker_thread: Optional[QThread] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.is_analyzing = False
        self.load_engines_from_config()
    
    def load_engines_from_config(self):
        """Load engines from configuration file"""
        config_file = Path("engines_config.json")
        if config_file.exists():
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.engines = [EngineInfo.from_dict(e) for e in data.get('engines', [])]
            except Exception as e:
                print(f"Failed to load engines config: {e}")
        
    def add_engine(self, name: str, path: str, protocol: str = "UCI") -> bool:
        """
        Add a new engine
        
        Args:
            name: Engine name
            path: Path to engine executable
            protocol: Engine protocol (UCI or WinBoard)
            
        Returns:
            True if successful
        """
        # Validate path
        engine_path = Path(path)
        if not engine_path.exists():
            self.engine_error.emit(f"Engine file not found: {path}")
            return False
            
        if not engine_path.suffix.lower() == ".exe":
            self.engine_error.emit(f"Invalid engine file: must be .exe")
            return False
            
        # Add engine
        engine_info = EngineInfo(name, path, protocol)
        self.engines.append(engine_info)
        return True
        
    def remove_engine(self, name: str):
        """Remove an engine by name"""
        self.engines = [e for e in self.engines if e.name != name]
        
    def get_engines(self) -> List[EngineInfo]:
        """Get list of available engines"""
        return self.engines.copy()
        
    def start_engine(self, engine_name: str):
        """Start an engine by name"""
        print(f"DEBUG: EngineManager.start_engine appelé avec {engine_name}")
        
        # Find engine
        engine = next((e for e in self.engines if e.name == engine_name), None)
        if not engine:
            print(f"DEBUG: Moteur {engine_name} non trouvé dans la liste")
            self.engine_error.emit(f"Engine not found: {engine_name}")
            return
        
        print(f"DEBUG: Moteur trouvé: {engine.name} à {engine.path}")
        print(f"DEBUG: Options UCI: {engine.options}")
            
        # Stop current engine if running
        if self.worker_thread and self.worker_thread.isRunning():
            print("DEBUG: Arrêt du moteur précédent")
            self.stop_engine()
        
        print("DEBUG: Création du worker et du thread")
        # Create worker and thread
        self.worker = EngineWorker()
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        print("DEBUG: Connexion des signaux")
        self.worker.analysis_update.connect(self._on_analysis_update)
        self.worker.engine_ready.connect(self._on_engine_ready)
        self.worker.engine_error.connect(self._on_engine_error)
        
        # Connect thread started to run_loop (event loop starts and runs forever)
        print("DEBUG: Connexion de thread.started à worker.run_loop")
        self.worker_thread.started.connect(self.worker.run_loop)
        
        # Store engine info for deferred start after loop is ready
        self.active_engine = engine
        print(f"DEBUG: Moteur actif défini: {self.active_engine.name}")
        
        # Start thread (this will start the event loop)
        print("DEBUG: Démarrage du thread avec event loop permanent")
        self.worker_thread.start()
        
        # The signal will be queued and processed once the worker thread's event loop is running
        # Using a small delay to ensure the loop has started
        import time
        time.sleep(0.2)  # 200ms delay
        
        print("DEBUG: Émission du signal start_requested")
        # Pass protocol in options dict with special key
        options_with_protocol = engine.options.copy()
        options_with_protocol["__protocol__"] = engine.protocol
        self.worker.start_requested.emit(engine.path, options_with_protocol)
        
    def _start_engine_async(self, engine_path: str):
        """Start engine asynchronously"""
        print(f"DEBUG: _start_engine_async appelé avec {engine_path}")
        
        # Run in a separate thread to avoid blocking Qt event loop
        import threading
        def run_engine():
            try:
                print("DEBUG: Création de l'event loop dans le thread")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                print("DEBUG: Appel de worker.start_engine")
                loop.run_until_complete(self.worker.start_engine(engine_path))
                print("DEBUG: worker.start_engine terminé")
                loop.close()
            except Exception as e:
                print(f"DEBUG: Exception dans _start_engine_async: {e}")
                self.engine_error.emit(f"Failed to start engine: {str(e)}")
        
        thread = threading.Thread(target=run_engine, daemon=True)
        thread.start()
        print("DEBUG: Thread de démarrage du moteur lancé")
            
    def stop_engine(self):
        """Stop the active engine"""
        print("DEBUG: EngineManager.stop_engine appelé")
        
        if self.worker:
            self.worker._stop_flag = True
            # Stop engine in its event loop if it exists
            if self.worker.loop and self.worker.engine:
                try:
                    print("DEBUG: Arrêt du moteur dans l'event loop")
                    asyncio.run_coroutine_threadsafe(
                        self.worker.stop_engine(),
                        self.worker.loop
                    ).result(timeout=2.0)
                except Exception as e:
                    print(f"DEBUG: Erreur lors de l'arrêt du moteur: {e}")
            
            # Stop the event loop
            if self.worker.loop and self.worker.loop.is_running():
                print("DEBUG: Arrêt de l'event loop permanent")
                self.worker.loop.call_soon_threadsafe(self.worker.loop.stop)
                
        if self.worker_thread:
            print("DEBUG: Arrêt du worker thread")
            self.worker_thread.quit()
            self.worker_thread.wait(2000)  # Wait max 2 seconds
            
        self.worker = None
        self.worker_thread = None
        self.active_engine = None
        self.is_analyzing = False
        self.engine_stopped.emit()
        print("DEBUG: Moteur arrêté")
        
    def analyze_position(self, board: chess.Board, multipv: int = 3, time_limit: float = 1.0):
        """
        Request position analysis
        
        Args:
            board: Chess board to analyze
            multipv: Number of variations to analyze
            time_limit: Time limit in seconds
        """
        print(f"DEBUG: EngineManager.analyze_position appelé")
        
        if not self.worker or not self.worker.loop:
            print("DEBUG: Pas de worker ou pas d'event loop")
            return
        
        # Check if either UCI or WinBoard engine is running
        if not self.worker.engine and not self.worker.winboard_engine:
            print("DEBUG: Pas de moteur démarré dans le worker")
            return
        
        print(f"DEBUG: Lancement analyse avec multipv={multipv}, time_limit={time_limit}")
        self.is_analyzing = True
        
        # Run analysis in the event loop
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.worker.analyze_position(board, multipv, time_limit),
                self.worker.loop
            )
            print("DEBUG: Coroutine d'analyse soumise à l'event loop")
        except Exception as e:
            print(f"DEBUG: Erreur lors de la soumission de l'analyse: {e}")
            import traceback
            traceback.print_exc()
        
    def stop_analysis(self):
        """Stop current analysis"""
        if self.worker:
            self.worker._stop_flag = True
        self.is_analyzing = False
    
    def update_option(self, name: str, value: any):
        """Update a UCI option on the fly"""
        if self.worker and self.worker.loop:
            print(f"DEBUG: EngineManager.update_option {name}={value}")
            asyncio.run_coroutine_threadsafe(
                self.worker.update_option(name, value),
                self.worker.loop
            )
            
            # Also update the active engine's options so they persist if saved
            if self.active_engine:
                self.active_engine.options[name] = value
    
    def get_best_move(self, board: chess.Board, time_limit: float = 2.0):
        """
        Get best move from engine
        
        Args:
            board: Chess board position
            time_limit: Time limit for search in seconds
            
        Returns:
            Future object that will contain the best move or None
        """
        print(f"DEBUG: EngineManager.get_best_move appelé")
        
        if not self.worker or not self.worker.loop:
            print("DEBUG: Pas de worker ou pas d'event loop")
            return None
        
        # Check if either UCI or WinBoard engine is running
        if not self.worker.engine and not self.worker.winboard_engine:
            print("DEBUG: Pas de moteur démarré dans le worker")
            return None
        
        print(f"DEBUG: Demande du meilleur coup avec time_limit={time_limit}")
        
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.worker.get_best_move(board, time_limit),
                self.worker.loop
            )
            # Add callback that emits signal (thread-safe)
            future.add_done_callback(self._on_move_ready)
            print("DEBUG: Coroutine get_best_move soumise à l'event loop")
            return future
        except Exception as e:
            print(f"ERROR: get_best_move submission failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _on_move_ready(self, future):
        """Internal callback that emits signal (thread-safe)"""
        try:
            move = future.result()
            print(f"DEBUG: _on_move_ready - move reçu: {move}")
            if move:
                print(f"DEBUG: Émission du signal move_ready")
                self.move_ready.emit(move)  # Signal is thread-safe
        except Exception as e:
            print(f"ERROR: _on_move_ready failed: {e}")
            import traceback
            traceback.print_exc()
            self.engine_error.emit(f"Move calculation error: {str(e)}")
        
    def _on_analysis_update(self, data: dict):
        """Handle analysis update from worker"""
        self.analysis_updated.emit(data)
        
    def _on_engine_ready(self, engine_name: str):
        """Handle engine ready signal"""
        print(f"DEBUG: EngineManager._on_engine_ready appelé avec engine_name={engine_name}")
        print(f"DEBUG: Émission du signal engine_started vers MainWindow")
        self.engine_started.emit(engine_name)
        print(f"DEBUG: Signal engine_started émis")
        
    def _on_engine_error(self, error_msg: str):
        """Handle engine error"""
        self.engine_error.emit(error_msg)
        
    def is_engine_running(self) -> bool:
        """Check if an engine is currently running"""
        return (self.worker is not None and 
                self.worker_thread is not None and 
                self.worker_thread.isRunning() and
                (self.worker.engine is not None or self.worker.winboard_engine is not None))
        
    def get_active_engine_name(self) -> Optional[str]:
        """Get the name of the active engine"""
        return self.active_engine.name if self.active_engine else None

