"""
Main window for ChessAvatar application
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QMenuBar, QMenu, QMessageBox, QSizePolicy, 
                             QFileDialog, QPushButton, QDialog, QDockWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
import chess
import asyncio

from ui.chessboard import ChessBoardWidget
from ui.notation_panel import NotationPanel
from ui.clock_widget import ClockWidget
from ui.engine_panel import EnginePanel
from ui.engine_config_dialog import EngineConfigDialog
from ui.avatar_panel import AvatarPanel, AvatarStatusWidget
from ui.avatar_creation_dialog import AvatarCreationDialog
from ui.board_config_dialog import BoardConfigDialog, BoardConfig
from ui.game_over_dialog import GameOverDialog
from ui.opening_panel import OpeningPanel  # NEW: Opening panel
from ui.theme_config_dialog import ThemeConfigDialog  # NEW: Theme config
from ui.new_game_dialog import NewGameDialog
from ui.styles import get_main_stylesheet, get_button_style  # NEW: Enhanced styles
from ui.resolution_manager import get_resolution_manager
from ui.layout_presets import LayoutPresets  # NEW: Layout presets
from ui.game_report_dialog import GameReportDialog  # NEW: Game report
from ui.about_dialog import AboutDialog  # NEW: About dialog
from ui.board_control_widget import BoardControlWidget  # NEW: Board controls
from core.game import ChessGame
from core.engine_manager import EngineManager
from core.avatar_manager import AvatarManager
from core.avatar_worker import AvatarEngineManager
from core.sound_manager import get_sound_manager
from core.pgn_manager import get_pgn_manager


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.res_mgr = get_resolution_manager()
        self.game = ChessGame()
        self.engine_manager = EngineManager()
        self.avatar_manager = AvatarManager()
        self.avatar_engine_manager = AvatarEngineManager()  # NEW: Avatar engine manager
        self.sound_manager = get_sound_manager()
        self.pgn_manager = get_pgn_manager()
        self.board_config = BoardConfig()
        self.playing_vs_avatar = False
        self.avatar_id = None  # Store current avatar ID
        self.avatar2_id = None  # Store second avatar ID (for Avatar vs Avatar mode)
        self.avatar2_stockfish_config = None  # Store second avatar config
        self._engine_auto_started = False  # Flag to ensure auto-start happens only once
        # Play vs engine mode
        self.play_mode = "free"  # "free", "vs_engine", "vs_avatar", "vs_human", "engine_vs_engine", "avatar_vs_avatar", "avatar_vs_engine"
        self.player_color = chess.WHITE  # Color of human player
        self.waiting_for_engine = False
        # Clock auto-start flag
        self.clock_started = False  # Flag pour savoir si la pendule a démarré
        self.setup_engine_signals()
        self.init_ui()
        # Theme is applied in init_ui() now
        self.apply_board_config()
    
    def showEvent(self, event):
        """Called when window is shown - use to auto-start engine after Qt event loop is running"""
        print("DEBUG: MainWindow.showEvent appelé")
        super().showEvent(event)
        # Auto-start engine on first show
        if not self._engine_auto_started:
            print("DEBUG: Premier showEvent, appel DIRECT de auto_start_engine")
            self._engine_auto_started = True
            # Call directly - the Qt event loop is running at this point
            try:
                self.auto_start_engine()
            except Exception as e:
                print(f"DEBUG: ERREUR dans auto_start_engine: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("DEBUG: showEvent suivant, auto_start déjà fait")
        
    def init_ui(self):
        """Initialize the user interface with dockable panels"""
        self.setWindowTitle("ChessAvatar - Analyse d'échecs")
        
        # Apply global stylesheet
        self.setStyleSheet(get_main_stylesheet())
        
        # Get optimal window size from resolution manager
        width, height = self.res_mgr.get_window_size()
        self.setGeometry(100, 100, width, height)
        
        # Enable docking features
        self.setDockNestingEnabled(True)  # Allow docks to be nested
        
        # ===== CENTRAL WIDGET: CHESSBOARD =====
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(5, 5, 5, 5)
        central_layout.setSpacing(5)
        
        # Chessboard
        self.chessboard = ChessBoardWidget()
        self.chessboard.set_board(self.game.board)
        self.chessboard.move_made.connect(self.on_move_made)
        self.chessboard.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        central_layout.addWidget(self.chessboard, stretch=10)
        
        # ===== DOCKABLE PANELS =====
        self._create_dock_widgets()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Status bar
        self.statusBar().showMessage("Prêt - Trait aux blancs")
        
        # Restore last window state (docks positions, sizes, etc.)
        self._restore_window_state()
    
    def _create_dock_widgets(self):
        """Create all dockable panels"""
        
        # ===== ENGINE PANEL (Bottom) =====
        self.engine_dock = QDockWidget("⚙ Moteur d'Analyse", self)
        self.engine_dock.setObjectName("EngineDock")
        self.engine_dock.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea | 
            Qt.DockWidgetArea.TopDockWidgetArea |
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        
        self.engine_panel = EnginePanel()
        self.engine_panel.start_analysis.connect(self.on_engine_start_analysis)
        self.engine_panel.stop_analysis.connect(self.on_engine_stop_analysis)
        self.engine_panel.option_changed.connect(self.on_engine_option_changed)
        self.engine_dock.setWidget(self.engine_panel)
        
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.engine_dock)
        
        # ===== OPENING PANEL (Bottom, next to engine) =====
        self.opening_dock = QDockWidget("📖 Ouverture", self)
        self.opening_dock.setObjectName("OpeningDock")
        self.opening_dock.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea | 
            Qt.DockWidgetArea.TopDockWidgetArea |
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        
        self.opening_panel = OpeningPanel()
        self.opening_dock.setWidget(self.opening_panel)
        
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.opening_dock)
        self.tabifyDockWidget(self.engine_dock, self.opening_dock)  # Tab them together
        
        # ===== NOTATION PANEL (Right) =====
        self.notation_dock = QDockWidget("📝 Notation", self)
        self.notation_dock.setObjectName("NotationDock")
        self.notation_dock.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea |
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.BottomDockWidgetArea |
            Qt.DockWidgetArea.TopDockWidgetArea
        )
        
        self.notation_panel = NotationPanel()
        self.notation_panel.move_selected.connect(self.on_navigate_to_move)
        self.notation_dock.setWidget(self.notation_panel)
        
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.notation_dock)
        
        # ===== AVATAR STATUS (Right, above notation) =====
        self.avatar_dock = QDockWidget("👤 Adversaire", self)
        self.avatar_dock.setObjectName("AvatarDock")
        self.avatar_dock.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea |
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.TopDockWidgetArea
        )
        
        self.avatar_status = AvatarStatusWidget()
        self.avatar_status.change_avatar_clicked.connect(self.manage_avatars)
        self.avatar_dock.setWidget(self.avatar_status)
        
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.avatar_dock)
        
        # ===== CLOCK WIDGET (Right, below notation) =====
        self.clock_dock = QDockWidget("⏱ Pendule", self)
        self.clock_dock.setObjectName("ClockDock")
        self.clock_dock.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea |
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.TopDockWidgetArea |
            Qt.DockWidgetArea.BottomDockWidgetArea
        )
        
        self.clock_widget = ClockWidget()
        self.clock_widget.time_expired.connect(self.on_time_expired)
        self.clock_dock.setWidget(self.clock_widget)
        
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.clock_dock)
        
        # ===== GAME CONTROLS (Right, bottom) =====
        self.controls_dock = QDockWidget("🎮 Contrôles", self)
        self.controls_dock.setObjectName("ControlsDock")
        self.controls_dock.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea |
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.BottomDockWidgetArea
        )
        
        game_controls_widget = QWidget()
        game_controls_layout = QHBoxLayout(game_controls_widget)
        game_controls_layout.setSpacing(8)
        game_controls_layout.setContentsMargins(5, 5, 5, 5)
        
        self.resign_button = QPushButton("⚐ Abandonner")
        self.resign_button.setToolTip("Abandonner la partie (Ctrl+R)")
        self.resign_button.clicked.connect(self.resign_game)
        self.resign_button.setStyleSheet(get_button_style('danger'))
        self.resign_button.setCursor(Qt.CursorShape.PointingHandCursor)
        game_controls_layout.addWidget(self.resign_button)
        
        self.draw_button = QPushButton("½ Nulle")
        self.draw_button.setToolTip("Proposer un match nul (Ctrl+D)")
        self.draw_button.clicked.connect(self.offer_draw)
        self.draw_button.setStyleSheet(get_button_style('warning'))
        self.draw_button.setCursor(Qt.CursorShape.PointingHandCursor)
        game_controls_layout.addWidget(self.draw_button)
        
        self.flip_button = QPushButton("⟲ Retourner")
        self.flip_button.setToolTip("Retourner l'échiquier (Ctrl+F)")
        self.flip_button.clicked.connect(self.flip_board_manual)
        self.flip_button.setStyleSheet(get_button_style('default'))
        self.flip_button.setCursor(Qt.CursorShape.PointingHandCursor)
        game_controls_layout.addWidget(self.flip_button)
        
        self.controls_dock.setWidget(game_controls_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.controls_dock)
        
        # Set initial visibility
        self.engine_dock.show()
        self.engine_dock.raise_()  # Bring engine tab to front
        
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # Jeu menu (simplifié, pas de redondances avec les boutons)
        game_menu = menubar.addMenu("📋 Jeu")
        
        new_game_action = QAction("🎯 Nouvelle partie", self)
        new_game_action.setShortcut("Ctrl+N")
        new_game_action.triggered.connect(self.new_game)
        game_menu.addAction(new_game_action)
        
        game_menu.addSeparator()
        
        open_pgn_action = QAction("📂 Ouvrir PGN...", self)
        open_pgn_action.setShortcut("Ctrl+O")
        open_pgn_action.triggered.connect(self.open_pgn)
        game_menu.addAction(open_pgn_action)
        
        save_pgn_action = QAction("💾 Sauvegarder PGN...", self)
        save_pgn_action.setShortcut("Ctrl+S")
        save_pgn_action.triggered.connect(self.save_pgn)
        game_menu.addAction(save_pgn_action)
        
        game_menu.addSeparator()
        
        copy_fen_action = QAction("📋 Copier FEN", self)
        copy_fen_action.setShortcut("Ctrl+Shift+C")
        copy_fen_action.triggered.connect(self.copy_fen)
        game_menu.addAction(copy_fen_action)
        
        paste_fen_action = QAction("📋 Coller FEN", self)
        paste_fen_action.setShortcut("Ctrl+Shift+V")
        paste_fen_action.triggered.connect(self.paste_fen)
        game_menu.addAction(paste_fen_action)
        
        game_menu.addSeparator()
        
        quit_action = QAction("🚪 Quitter", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        game_menu.addAction(quit_action)
        
        # Apparence menu
        appearance_menu = menubar.addMenu("🎨 Apparence")
        
        theme_config_action = QAction("🖌️ Thèmes et Pièces...", self)
        theme_config_action.setShortcut("Ctrl+T")
        theme_config_action.triggered.connect(self.open_theme_config)
        appearance_menu.addAction(theme_config_action)
        
        appearance_menu.addSeparator()
        
        board_config_action = QAction("⚙️ Configuration de l'échiquier...", self)
        board_config_action.triggered.connect(self.open_board_config)
        appearance_menu.addAction(board_config_action)
        
        # NEW: Affichage menu with layout presets and dock toggles
        display_menu = menubar.addMenu("🖥️ Affichage")
        
        # Dock visibility toggles
        docks_submenu = QMenu("📐 Panneaux", self)
        
        self.engine_dock_action = self.engine_dock.toggleViewAction()
        self.engine_dock_action.setText("⚙ Moteur d'Analyse")
        docks_submenu.addAction(self.engine_dock_action)
        
        self.opening_dock_action = self.opening_dock.toggleViewAction()
        self.opening_dock_action.setText("📖 Ouverture")
        docks_submenu.addAction(self.opening_dock_action)
        
        self.notation_dock_action = self.notation_dock.toggleViewAction()
        self.notation_dock_action.setText("📝 Notation")
        docks_submenu.addAction(self.notation_dock_action)
        
        self.avatar_dock_action = self.avatar_dock.toggleViewAction()
        self.avatar_dock_action.setText("👤 Adversaire")
        docks_submenu.addAction(self.avatar_dock_action)
        
        self.clock_dock_action = self.clock_dock.toggleViewAction()
        self.clock_dock_action.setText("⏱ Pendule")
        docks_submenu.addAction(self.clock_dock_action)
        
        self.controls_dock_action = self.controls_dock.toggleViewAction()
        self.controls_dock_action.setText("🎮 Contrôles")
        docks_submenu.addAction(self.controls_dock_action)
        
        display_menu.addMenu(docks_submenu)
        display_menu.addSeparator()
        
        # Layout reset
        reset_layout_action = QAction("↺ Réinitialiser la disposition", self)
        reset_layout_action.setShortcut("Ctrl+Shift+R")
        reset_layout_action.triggered.connect(self._reset_layout)
        display_menu.addAction(reset_layout_action)
        
        save_layout_action = QAction("💾 Sauvegarder la disposition", self)
        save_layout_action.triggered.connect(self._save_window_state)
        display_menu.addAction(save_layout_action)
        
        # Analyse menu (simplifié)
        analysis_menu = menubar.addMenu("📊 Analyse")
        
        undo_action = QAction("↶ Annuler le coup", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo_move)
        analysis_menu.addAction(undo_action)
        
        analysis_menu.addSeparator()
        
        # NEW: Game report
        game_report_action = QAction("📄 Rapport de partie...", self)
        game_report_action.setShortcut("Ctrl+R")
        game_report_action.triggered.connect(self.show_game_report)
        analysis_menu.addAction(game_report_action)
        
        # Moteur menu
        engine_menu = menubar.addMenu("⚙️ Moteur")
        
        engine_settings_action = QAction("🔧 Configuration des moteurs...", self)
        engine_settings_action.triggered.connect(self.open_engine_config)
        engine_menu.addAction(engine_settings_action)
        
        engine_menu.addSeparator()
        
        # Submenu for selecting engine
        self.select_engine_menu = QMenu("🎯 Sélectionner le moteur", self)
        engine_menu.addMenu(self.select_engine_menu)
        self.update_engine_menu()
        
        # Avatar menu
        avatar_menu = menubar.addMenu("🤖 Avatar")
        
        create_avatar_action = QAction("➕ Créer un Avatar IA...", self)
        create_avatar_action.setShortcut("Ctrl+Shift+A")
        create_avatar_action.triggered.connect(self.create_avatar)
        avatar_menu.addAction(create_avatar_action)
        
        manage_avatars_action = QAction("📁 Gérer les Avatars...", self)
        manage_avatars_action.triggered.connect(self.manage_avatars)
        avatar_menu.addAction(manage_avatars_action)
        
        # NEW: Help/About menu
        help_menu = menubar.addMenu("❓ Aide")
        
        about_action = QAction("ℹ️ À propos de ChessAvatar...", self)
        about_action.setShortcut("F1")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_engine_signals(self):
        """Setup engine manager signals"""
        self.engine_manager.engine_started.connect(self.on_engine_started)
        self.engine_manager.engine_stopped.connect(self.on_engine_stopped)
        self.engine_manager.engine_error.connect(self.on_engine_error)
        self.engine_manager.analysis_updated.connect(self.on_analysis_updated)
        self.engine_manager.move_ready.connect(self.on_engine_move_ready)  # Engine vs mode
        
        # Avatar engine signals
        self.avatar_engine_manager.avatar_started.connect(self.on_avatar_started)
        self.avatar_engine_manager.avatar_stopped.connect(self.on_avatar_stopped)
        self.avatar_engine_manager.avatar_error.connect(self.on_avatar_error)
        self.avatar_engine_manager.move_ready.connect(self.on_avatar_move_ready)  # Avatar vs mode
    
    def auto_start_engine(self):
        """Automatically start the first available engine at startup"""
        print("DEBUG: auto_start_engine VRAIMENT appele")
        print("DEBUG: auto_start_engine appelé")
        engines = self.engine_manager.get_engines()
        print(f"DEBUG: Moteurs trouvés: {len(engines)}")
        
        if engines:
            # Start the first engine automatically
            print(f"DEBUG: Démarrage du moteur {engines[0].name}")
            self.start_engine(engines[0].name)
        else:
            # Show helpful message
            print("DEBUG: Aucun moteur trouvé")
            self.engine_panel.set_engine_status("Non configuré")
            self.engine_panel.engine_status.setStyleSheet("color: #ff6b6b; font-size: 9pt;")
            self.statusBar().showMessage(
                "💡 Configurez un moteur: Menu → Moteur → Configuration des moteurs", 
                10000
            )
        
    def on_move_made(self, from_square: int, to_square: int):
        """Handle move made on the board"""
        # Check if it's player's turn when playing vs engine
        if self.play_mode == "vs_engine":
            if self.waiting_for_engine:
                self.statusBar().showMessage("Attendez que le moteur joue!", 2000)
                self.chessboard.set_board(self.game.board)
                return
            # Check if it's the player's turn
            if self.game.board.turn != self.player_color:
                # Cancel the move
                self.chessboard.set_board(self.game.board)
                self.statusBar().showMessage("Ce n'est pas votre tour !", 2000)
                return
        
        # Check if it's player's turn when playing vs avatar
        if self.play_mode == "vs_avatar":
            # Check if it's the player's turn
            if self.game.board.turn != self.player_color:
                # Cancel the move
                self.chessboard.set_board(self.game.board)
                self.statusBar().showMessage("Ce n'est pas votre tour !", 2000)
                return
        
        # Create move
        move = chess.Move(from_square, to_square)
        
        # Check if it's a pawn promotion
        piece = self.game.board.piece_at(from_square)
        if piece and piece.piece_type == chess.PAWN:
            if chess.square_rank(to_square) in [0, 7]:
                move = chess.Move(from_square, to_square, chess.QUEEN)
        
        # Make the move
        if self.game.make_move(move):
            # Auto-start clock after first White move
            if not self.clock_started and len(self.game.board.move_stack) == 1:
                print("DEBUG: Premier coup des Blancs - démarrage de la pendule")
                self.clock_widget.start()
                self.clock_started = True
            
            # Switch clock if active
            if self.clock_widget.timer.isActive():
                self.clock_widget.switch_clock()
            
            # Update notation panel
            pgn_text = self.game.get_pgn_moves()
            self.notation_panel.update_moves(pgn_text)
            
            # Play appropriate sound
            if self.game.board.is_capture(move):
                self.sound_manager.play_capture()
            elif self.game.board.is_castling(move):
                self.sound_manager.play_castle()
            elif self.game.board.is_check():
                self.sound_manager.play_check()
            else:
                self.sound_manager.play_move()
            
            # Update the board display
            self.chessboard.set_board(self.game.board)
            
            # NEW: Update opening panel
            self.opening_panel.update_opening(self.game.board)
            
            # Update notation
            pgn_text = self.game.get_pgn_moves()
            self.notation_panel.update_moves(pgn_text)
            
            # Update status bar
            if self.game.is_game_over():
                result = self.game.get_result()
                reason = self.get_game_over_reason()
                self.statusBar().showMessage(f"Partie terminée - {result}")
                self.notation_panel.set_game_info(f"Partie terminée - {result}")
                self.sound_manager.play_game_end()
                # Stop engine analysis
                if self.engine_manager.is_analyzing:
                    self.engine_manager.stop_analysis()
                # Stop avatar game
                if self.playing_vs_avatar:
                    self.playing_vs_avatar = False
                # Stop vs engine game
                if self.play_mode == "vs_engine":
                    self.play_mode = "free"
                    self.waiting_for_engine = False
                # Show game over dialog
                self.show_game_over_dialog(result, reason)
            else:
                # Check if king is in check
                if self.game.board.is_check():
                    self.sound_manager.play_check()
                
                turn = "Trait aux blancs" if self.game.board.turn == chess.WHITE else "Trait aux noirs"
                self.statusBar().showMessage(turn)
                
                # Auto-analyze if engine is running
                if self.engine_manager.is_engine_running() and self.engine_panel.is_analyzing:
                    self.request_analysis()
                
                # Trigger engine move if playing vs engine
                if self.play_mode == "vs_engine" and not self.game.board.is_game_over():
                    self.request_engine_move()
                
                # Trigger avatar move if playing vs avatar
                if self.play_mode == "vs_avatar" and not self.game.board.is_game_over():
                    self.request_avatar_move()
                
            # Switch clock
            if self.clock_widget.timer.isActive():
                self.clock_widget.switch_clock()
                
    def new_game(self):
        """Start a new game"""
        # Get list of available avatars for dialog
        avatars = self.avatar_manager.get_all_avatars()
        avatar_available = len(avatars) > 0
        
        # Get list of engines
        engines = self.engine_manager.get_engines()
        
        # Show configuration dialog
        dialog = NewGameDialog(
            engine_available=self.engine_manager.is_engine_running(),
            avatar_available=avatar_available,
            avatars=avatars,  # Pass avatar list
            engines=engines,  # Pass engine list
            parent=self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_config()
            
            # Stop any active avatar
            if self.avatar_engine_manager.is_avatar_running():
                self.avatar_engine_manager.stop_avatar()
            
            # Reset game
            self.game.reset()
            self.chessboard.set_board(self.game.board)
            self.notation_panel.clear()
            self.notation_panel.set_game_info("Nouvelle partie")
            self.clock_widget.reset()
            self.clock_started = False  # Reset clock flag
            self.engine_panel.reset_analysis()
            
            # Apply time control if changed
            if config['time_control']:
                self.clock_widget.time_control_combo.setCurrentText(config['time_control'])
            
            # Configure mode
            if config['mode'] == "vs_engine":
                self.player_color = config['player_color']
                self.play_mode = "vs_engine"
                self.waiting_for_engine = False
                self.playing_vs_avatar = False
                
                # Clear avatar status
                self.avatar_status.clear()
                
                # Switch to selected engine if specified
                selected_engine = config.get('engine_name')
                if selected_engine:
                    current_engine = self.engine_manager.get_active_engine_name()
                    if current_engine != selected_engine:
                        print(f"DEBUG: Changement de moteur vers {selected_engine}")
                        self.start_engine(selected_engine)
                
                # Flip board if playing as Black
                if self.player_color == chess.BLACK and not self.chessboard.flipped:
                    self.chessboard.flip_board()
                elif self.player_color == chess.WHITE and self.chessboard.flipped:
                    self.chessboard.flip_board()
                
                # If Black, engine plays first
                if self.player_color == chess.BLACK:
                    self.chessboard.setEnabled(False)
                    self.request_engine_move()
                    self.statusBar().showMessage("Nouvelle partie contre le moteur - Le moteur réfléchit...", 5000)
                else:
                    self.chessboard.setEnabled(True)
                    self.statusBar().showMessage(
                        f"Nouvelle partie contre le moteur - Vous jouez les Blancs",
                        5000
                    )
            elif config['mode'] == "vs_avatar":
                # Avatar mode
                avatar_id = config.get('avatar_id')
                if not avatar_id:
                    QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un avatar")
                    return
                
                self.player_color = config['player_color']
                self.play_mode = "vs_avatar"
                self.waiting_for_engine = False
                self.playing_vs_avatar = True
                self.avatar_id = avatar_id
                
                # Get avatar info
                avatar = self.avatar_manager.get_avatar(avatar_id)
                if not avatar:
                    QMessageBox.warning(self, "Erreur", "Avatar non trouvé")
                    return
                
                # Set avatar status display
                self.avatar_status.set_avatar(avatar)
                
                # Get player style for avatar
                player_style = self.avatar_manager.get_player_style(avatar_id)
                if not player_style:
                    QMessageBox.warning(self, "Erreur", "Style du joueur non disponible")
                    return
                
                # Get Stockfish path
                engines = self.engine_manager.get_engines()
                stockfish = next((e for e in engines if 'stockfish' in e.name.lower()), None)
                
                if not stockfish:
                    QMessageBox.warning(
                        self,
                        "Moteur Requis",
                        "Veuillez d'abord configurer Stockfish dans\n"
                        "Menu → Moteur → Configuration des moteurs"
                    )
                    return
                
                # Start avatar engine
                print(f"DEBUG: Démarrage de l'avatar {avatar.display_name}")
                self.avatar_engine_manager.start_avatar(avatar_id, stockfish.path, player_style)
                
                # Flip board if playing as Black
                if self.player_color == chess.BLACK and not self.chessboard.flipped:
                    self.chessboard.flip_board()
                elif self.player_color == chess.WHITE and self.chessboard.flipped:
                    self.chessboard.flip_board()
                
                # If Black, avatar plays first
                if self.player_color == chess.BLACK:
                    self.chessboard.setEnabled(False)
                    # Request avatar move after a short delay (wait for engine to start)
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(1000, lambda: self.request_avatar_move())
                    self.statusBar().showMessage(f"Nouvelle partie contre {avatar.display_name} - L'avatar réfléchit...", 5000)
                else:
                    self.chessboard.setEnabled(True)
                    self.statusBar().showMessage(
                        f"Nouvelle partie contre {avatar.display_name} - Vous jouez les Blancs",
                        5000
                    )
            elif config['mode'] == "engine_vs_engine":
                # Engine vs Engine mode
                self.play_mode = "engine_vs_engine"
                self.waiting_for_engine = False
                self.playing_vs_avatar = False
                self.chessboard.setEnabled(False)  # Disable user input
                
                # Clear avatar status
                self.avatar_status.clear()
                
                # Reset board orientation
                if self.chessboard.flipped:
                    self.chessboard.flip_board()
                
                self.statusBar().showMessage("⚔️ Moteur vs Moteur - Observation", 3000)
                
                # Start with White (engine) making first move
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(1000, lambda: self.auto_play_engine_move())
                
            elif config['mode'] == "avatar_vs_avatar":
                # Avatar vs Avatar mode
                avatar_id = config.get('avatar_id')
                avatar2_id = config.get('avatar2_id')
                
                if not avatar_id or not avatar2_id:
                    QMessageBox.warning(self, "Erreur", "Veuillez sélectionner deux avatars")
                    return
                
                if avatar_id == avatar2_id:
                    QMessageBox.warning(self, "Erreur", "Veuillez sélectionner deux avatars différents")
                    return
                
                # Get avatars
                avatar1 = self.avatar_manager.get_avatar(avatar_id)
                avatar2 = self.avatar_manager.get_avatar(avatar2_id)
                
                if not avatar1 or not avatar2:
                    QMessageBox.warning(self, "Erreur", "Avatar introuvable")
                    return
                
                self.play_mode = "avatar_vs_avatar"
                self.waiting_for_engine = False
                self.playing_vs_avatar = True
                self.chessboard.setEnabled(False)  # Disable user input
                self.avatar_id = avatar_id
                self.avatar2_id = avatar2_id
                
                # Start both avatars
                # Get Stockfish path
                engines = self.engine_manager.get_engines()
                if not engines:
                    QMessageBox.warning(self, "Erreur", "Aucun moteur configuré")
                    return
                stockfish = engines[0]
                
                # Start avatar 1 (White)
                player1_style = self.avatar_manager.get_player_style(avatar_id)
                self.avatar_engine_manager.start_avatar(avatar_id, stockfish.path, player1_style)
                
                # Store avatar 2 info for when it's their turn
                self.avatar2_stockfish_config = self.avatar_manager.get_player_style(avatar2_id)
                
                # Update status
                self.avatar_status.setText(f"⚔️ {avatar1.display_name} (Blancs) vs {avatar2.display_name} (Noirs)")
                
                # Reset board
                if self.chessboard.flipped:
                    self.chessboard.flip_board()
                
                self.statusBar().showMessage(
                    f"👥 {avatar1.display_name} vs {avatar2.display_name} - Observation",
                    5000
                )
                
                # Avatar 1 (White) plays first
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(1500, lambda: self.auto_play_avatar_move())
                
            elif config['mode'] == "avatar_vs_engine":
                # Avatar vs Engine mode
                avatar_id = config.get('avatar_id')
                
                if not avatar_id:
                    QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un avatar")
                    return
                
                # Get avatar
                avatar = self.avatar_manager.get_avatar(avatar_id)
                if not avatar:
                    QMessageBox.warning(self, "Erreur", "Avatar introuvable")
                    return
                
                self.play_mode = "avatar_vs_engine"
                self.waiting_for_engine = False
                self.playing_vs_avatar = True
                self.chessboard.setEnabled(False)  # Disable user input
                self.avatar_id = avatar_id
                
                # Get Stockfish path
                engines = self.engine_manager.get_engines()
                if not engines:
                    QMessageBox.warning(self, "Erreur", "Aucun moteur configuré")
                    return
                stockfish = engines[0]
                
                # Start avatar (will play as White)
                player_style = self.avatar_manager.get_player_style(avatar_id)
                self.avatar_engine_manager.start_avatar(avatar_id, stockfish.path, player_style)
                
                # Update status
                self.avatar_status.setText(f"🤖 {avatar.display_name} (Avatar) vs Moteur")
                
                # Reset board
                if self.chessboard.flipped:
                    self.chessboard.flip_board()
                
                self.statusBar().showMessage(
                    f"🤖 {avatar.display_name} vs Moteur - Observation",
                    5000
                )
                
                # Avatar (White) plays first
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(1500, lambda: self.request_avatar_move())
                
            else:
                # Free mode or Human vs Human mode
                self.play_mode = config['mode']  # Can be "free" or "vs_human"
                self.waiting_for_engine = False
                self.playing_vs_avatar = False
                self.chessboard.setEnabled(True)
                
                # Clear avatar status
                self.avatar_status.clear()
                
                # Reset board orientation to default (White at bottom)
                if self.chessboard.flipped:
                    self.chessboard.flip_board()
                
                if config['mode'] == "vs_human":
                    self.statusBar().showMessage("Nouvelle partie - Humain vs Humain (local)", 3000)
                else:
                    self.statusBar().showMessage("Nouvelle partie - Mode libre", 3000)
            
    def open_pgn(self):
        """Open PGN file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un fichier PGN",
            "",
            "Fichiers PGN (*.pgn);;Tous les fichiers (*.*)"
        )
        
        if file_path:
            game = self.pgn_manager.import_game(file_path)
            if game:
                # Get moves from game
                moves = self.pgn_manager.game_to_move_list(game)
                game_info = self.pgn_manager.get_game_info(game)
                
                # Reset board and replay moves
                self.game.reset()
                self.chessboard.set_board(self.game.board)
                
                # Apply moves
                for move_san in moves:
                    try:
                        move = self.game.board.parse_san(move_san)
                        self.game.make_move(move)
                    except:
                        break
                        
                # Update display
                self.chessboard.set_board(self.game.board)
                pgn_text = self.game.get_pgn_moves()
                self.notation_panel.update_moves(pgn_text)
                
                # Show game info
                info_text = f"{game_info['white']} vs {game_info['black']}\n"
                info_text += f"{game_info['event']} - {game_info['date']}"
                self.notation_panel.set_game_info(info_text)
                
                self.statusBar().showMessage(f"PGN chargé: {len(moves)} coups", 3000)
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de charger le fichier PGN")
        
    def save_pgn(self):
        """Save game as PGN"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder en PGN",
            "",
            "Fichiers PGN (*.pgn);;Tous les fichiers (*.*)"
        )
        
        if file_path:
            # Add .pgn extension if not present
            if not file_path.endswith('.pgn'):
                file_path += '.pgn'
                
            success = self.pgn_manager.export_game(
                self.game.board,
                self.game.move_history,
                file_path,
                white_player="Joueur 1",
                black_player="Joueur 2",
                result=self.game.board.result() if self.game.is_game_over() else "*"
            )
            
            if success:
                self.statusBar().showMessage(f"Partie sauvegardée: {file_path}", 3000)
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de sauvegarder le fichier")
        
    def flip_board(self):
        """Flip the board orientation"""
        self.chessboard.flip_board()
        
    def copy_fen(self):
        """Copy FEN to clipboard (placeholder)"""
        from PyQt6.QtWidgets import QApplication
        fen = self.game.board.fen()
        QApplication.clipboard().setText(fen)
        self.statusBar().showMessage(f"FEN copié: {fen}", 3000)
        
    def paste_fen(self):
        """Paste FEN from clipboard (placeholder)"""
        QMessageBox.information(
            self,
            "Coller FEN",
            "Fonctionnalité à venir dans une prochaine version"
        )
        
    def undo_move(self):
        """Undo the last move"""
        if self.game.undo_move():
            self.chessboard.set_board(self.game.board)
            pgn_text = self.game.get_pgn_moves()
            self.notation_panel.update_moves(pgn_text)
            turn = "Trait aux blancs" if self.game.board.turn == chess.WHITE else "Trait aux noirs"
            self.statusBar().showMessage(turn)
            
            # Re-analyze position if engine is analyzing
            if self.engine_manager.is_analyzing:
                self.request_analysis()
                
    def open_engine_config(self):
        """Open engine configuration dialog"""
        engines = self.engine_manager.get_engines()
        dialog = EngineConfigDialog(engines, self)
        dialog.engines_changed.connect(self.on_engines_changed)
        
        if dialog.exec():
            # Update engines in manager
            new_engines = dialog.get_engines()
            self.engine_manager.engines = new_engines
            self.update_engine_menu()
            
    def update_engine_menu(self):
        """Update the engine selection menu"""
        self.select_engine_menu.clear()
        
        engines = self.engine_manager.get_engines()
        if not engines:
            no_engine_action = QAction("Aucun moteur configuré", self)
            no_engine_action.setEnabled(False)
            self.select_engine_menu.addAction(no_engine_action)
        else:
            for engine in engines:
                action = QAction(engine.name, self)
                action.triggered.connect(lambda checked, name=engine.name: self.select_engine(name))
                self.select_engine_menu.addAction(action)
                
    def on_engines_changed(self):
        """Handle engines list change"""
        self.update_engine_menu()
        
    def select_engine(self, engine_name: str):
        """Select and start an engine"""
        self.start_engine(engine_name)
        
    def start_engine(self, engine_name: str = None):
        """Start the selected engine"""
        print(f"DEBUG: start_engine appelé avec engine_name={engine_name}")
        
        if engine_name is None:
            # Get first available engine
            engines = self.engine_manager.get_engines()
            if not engines:
                QMessageBox.warning(
                    self,
                    "Aucun moteur",
                    "Veuillez d'abord configurer un moteur d'échecs."
                )
                return
            engine_name = engines[0].name
        
        print(f"DEBUG: Appel de engine_manager.start_engine({engine_name})")
        self.engine_manager.start_engine(engine_name)
        self.statusBar().showMessage(f"Démarrage du moteur {engine_name}...", 3000)
        
    def stop_engine(self):
        """Stop the current engine"""
        if self.engine_manager.is_engine_running():
            engine_name = self.engine_manager.get_active_engine_name()
            self.engine_manager.stop_engine()
            self.statusBar().showMessage(f"Moteur {engine_name} arrêté", 3000)
    
    def toggle_play_vs_engine(self, checked: bool):
        """Toggle play vs engine mode"""
        if checked:
            # Check if engine is running
            if not self.engine_manager.is_engine_running():
                QMessageBox.warning(
                    self,
                    "Moteur non démarré",
                    "Veuillez d'abord démarrer un moteur pour jouer contre lui."
                )
                return
            
            # Ask player to choose color
            from PyQt6.QtWidgets import QInputDialog
            items = ["Blancs", "Noirs"]
            item, ok = QInputDialog.getItem(
                self, 
                "Choisir votre couleur",
                "Avec quelle couleur voulez-vous jouer ?",
                items, 
                0, 
                False
            )
            
            if ok and item:
                self.player_color = chess.WHITE if item == "Blancs" else chess.BLACK
                self.play_mode = "vs_engine"
                self.waiting_for_engine = False
                
                print(f"DEBUG: player_color défini à {self.player_color}")
                print(f"DEBUG: Mode vs_engine activé")
                
                # Auto-flip board based on player color
                if self.player_color == chess.BLACK and not self.chessboard.flipped:
                    print(f"DEBUG: Flip board (Noirs en bas)")
                    self.chessboard.flip_board()
                elif self.player_color == chess.WHITE and self.chessboard.flipped:
                    print(f"DEBUG: Flip board (Blancs en bas)")
                    self.chessboard.flip_board()
                
                # Start new game
                self.new_game()
                print(f"DEBUG: Nouveau jeu démarré, turn={self.game.board.turn}")
                
                # If player chose black, engine plays first
                if self.player_color == chess.BLACK:
                    print(f"DEBUG: Appel request_engine_move (moteur joue Blancs)")
                    # Disable board interaction until engine plays
                    self.chessboard.setEnabled(False)
                    self.statusBar().showMessage("Le moteur joue en premier...", 0)
                    self.request_engine_move()
                else:
                    self.statusBar().showMessage("Mode: Jouer contre le moteur - À vous de jouer!", 3000)
        else:
            # Disable vs engine mode
            self.play_mode = "free"
            self.waiting_for_engine = False
            self.statusBar().showMessage("Mode libre activé", 2000)
    
    def request_engine_move(self):
        """Request and play engine's move"""
        if not self.engine_manager.is_engine_running():
            self.statusBar().showMessage("Moteur non disponible", 2000)
            return
        
        # Get engine name for display
        engine_name = self.engine_manager.get_active_engine_name() or "Moteur"
        
        self.waiting_for_engine = True
        self.statusBar().showMessage(f"⚙️ {engine_name} réfléchit...", 0)
        
        # Request best move from engine
        # The move_ready signal will be emitted automatically
        self.engine_manager.get_best_move(self.game.board, time_limit=2.0)
    
    def request_avatar_move(self):
        """Request and play avatar's move"""
        if not self.avatar_engine_manager.is_avatar_running():
            self.statusBar().showMessage("Avatar non disponible", 2000)
            return
        
        # Disable board while avatar is thinking
        self.chessboard.setEnabled(False)
        
        # Get avatar info for display
        avatar = self.avatar_manager.get_avatar(self.avatar_id)
        avatar_name = avatar.display_name if avatar else "Avatar"
        
        self.statusBar().showMessage(f"{avatar_name} réfléchit...", 0)
        
        # Request best move from avatar
        # The move_ready signal will be emitted automatically
        self.avatar_engine_manager.request_move(self.game.board, time_limit=2.0)
    
    def request_avatar2_move(self):
        """Request and play second avatar's move (for Avatar vs Avatar mode)"""
        if not hasattr(self, 'avatar2_id'):
            return
        
        # Stop current avatar engine
        if self.avatar_engine_manager.is_avatar_running():
            self.avatar_engine_manager.stop_avatar()
        
        # Start avatar 2
        engines = self.engine_manager.get_all_engines()
        if engines:
            stockfish = engines[0]
            avatar2 = self.avatar_manager.get_avatar(self.avatar2_id)
            if avatar2:
                self.avatar_engine_manager.start_avatar(
                    self.avatar2_id,
                    stockfish.path,
                    self.avatar2_stockfish_config
                )
                
                # Wait a bit for engine to start, then request move
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(500, lambda: self._request_avatar2_move_delayed(avatar2))
    
    def _request_avatar2_move_delayed(self, avatar2):
        """Delayed avatar 2 move request"""
        self.chessboard.setEnabled(False)
        self.statusBar().showMessage(f"{avatar2.display_name} réfléchit...", 0)
        self.avatar_engine_manager.request_move(self.game.board, time_limit=2.0)
        
        # After avatar 2 moves, switch back to avatar 1 for next turn
        # This will be handled in on_avatar_move_ready
    
    def auto_play_engine_move(self):
        """Auto-play engine move for Engine vs Engine mode"""
        if not self.engine_manager.is_engine_running():
            self.statusBar().showMessage("Moteur non disponible", 2000)
            return
        
        # Request move from engine
        self.chessboard.setEnabled(False)
        turn_name = "Blancs" if self.game.board.turn == chess.WHITE else "Noirs"
        self.statusBar().showMessage(f"⚙️ Moteur ({turn_name}) réfléchit...", 0)
        self.request_engine_move()
    
    def auto_play_avatar_move(self):
        """Auto-play avatar move for Avatar vs Avatar mode"""
        # For Avatar vs Avatar, we need to switch avatars
        if self.play_mode == "avatar_vs_avatar":
            turn = self.game.board.turn
            
            # Stop current avatar
            if self.avatar_engine_manager.is_avatar_running():
                self.avatar_engine_manager.stop_avatar()
            
            engines = self.engine_manager.get_engines()
            if not engines:
                self.statusBar().showMessage("Aucun moteur disponible", 2000)
                return
            
            stockfish = engines[0]
            
            if turn == chess.WHITE:
                # White's turn (avatar1)
                avatar = self.avatar_manager.get_avatar(self.avatar_id)
                if avatar:
                    self.statusBar().showMessage(f"🤖 {avatar.display_name} (Blancs) réfléchit...", 0)
                    # Restart with avatar1 config
                    player_style = self.avatar_manager.get_player_style(self.avatar_id)
                    self.avatar_engine_manager.start_avatar(self.avatar_id, stockfish.path, player_style)
                    # Wait for engine to start
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(500, lambda: self.request_avatar_move())
                    return
            else:
                # Black's turn (avatar2)
                avatar2 = self.avatar_manager.get_avatar(self.avatar2_id)
                if avatar2:
                    self.statusBar().showMessage(f"🤖 {avatar2.display_name} (Noirs) réfléchit...", 0)
                    # Restart with avatar2 config
                    self.avatar_engine_manager.start_avatar(
                        self.avatar2_id,
                        stockfish.path,
                        self.avatar2_stockfish_config
                    )
                    # Wait for engine to start
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(500, lambda: self.request_avatar_move())
                    return
        
        # Single avatar mode - just request move
        if not self.avatar_engine_manager.is_avatar_running():
            self.statusBar().showMessage("Avatar non disponible", 2000)
            return
        
        self.request_avatar_move()
    
    def on_engine_move_ready(self, move):
        """Handle engine move result (called from signal, thread-safe)"""
        print(f"DEBUG: on_engine_move_ready appelé avec move={move}")
        
        if not move:
            self.waiting_for_engine = False
            # Re-enable board if it was disabled
            self.chessboard.setEnabled(True)
            self.statusBar().showMessage("Erreur: coup invalide", 2000)
            return
        
        try:
            # Play the move on the board
            if self.game.make_move(move):
                # Update notation panel
                pgn_text = self.game.get_pgn_moves()
                self.notation_panel.update_moves(pgn_text)
                
                # Play appropriate sound
                if self.game.board.is_capture(move):
                    self.sound_manager.play_capture()
                elif self.game.board.is_castling(move):
                    self.sound_manager.play_castle()
                elif self.game.board.is_check():
                    self.sound_manager.play_check()
                else:
                    self.sound_manager.play_move()
                
                # Update the board display
                self.chessboard.set_board(self.game.board)
                
                # Check game over
                if self.game.is_game_over():
                    result = self.game.get_result()
                    reason = self.get_game_over_reason()
                    self.statusBar().showMessage(f"Partie terminée - {result}")
                    self.notation_panel.set_game_info(f"Partie terminée - {result}")
                    self.sound_manager.play_game_end()
                    self.play_mode = "free"
                    # Show game over dialog
                    self.show_game_over_dialog(result, reason)
                else:
                    # Handle AI vs AI modes
                    if self.play_mode == "engine_vs_engine":
                        # Engine vs Engine: continue playing
                        from PyQt6.QtCore import QTimer
                        QTimer.singleShot(800, lambda: self.auto_play_engine_move())
                        self.statusBar().showMessage(f"Stockfish joue: {move.uci()}", 2000)
                    elif self.play_mode == "avatar_vs_engine":
                        # Avatar vs Engine
                        if self.game.board.turn == chess.WHITE:
                            # Avatar's turn
                            from PyQt6.QtCore import QTimer
                            QTimer.singleShot(800, lambda: self.request_avatar_move())
                        else:
                            # Engine's turn (just played, so re-enable for next cycle)
                            self.chessboard.setEnabled(False)
                    else:
                        # Normal mode: Re-enable board interaction after engine move
                        self.chessboard.setEnabled(True)
                        print(f"DEBUG: Échiquier réactivé, turn={self.game.board.turn}")
                        self.statusBar().showMessage(f"Stockfish joue : {move.uci()} - À vous de jouer!", 3000)
        except Exception as e:
            print(f"ERROR: Engine move failed: {e}")
            import traceback
            traceback.print_exc()
            self.statusBar().showMessage("Erreur du moteur", 3000)
            # Re-enable board on error
            self.chessboard.setEnabled(True)
        finally:
            self.waiting_for_engine = False
        
    def on_engine_started(self, engine_name: str):
        """Handle engine started signal"""
        print(f"DEBUG: MainWindow.on_engine_started appelé avec engine_name={engine_name}")
        
        # Get UCI options from the active engine
        active_engine = self.engine_manager.active_engine
        uci_options = active_engine.options if active_engine else None
        
        print(f"DEBUG: Active engine: {active_engine.name if active_engine else 'None'}")
        print(f"DEBUG: UCI options: {uci_options}")
        
        # Update engine panel with status and UCI options
        print(f"DEBUG: Appel de engine_panel.set_engine_status({engine_name}, {uci_options})")
        self.engine_panel.set_engine_status(engine_name, uci_options)
        print(f"DEBUG: engine_panel.set_engine_status terminé")
        
        self.statusBar().showMessage(f"Moteur {engine_name} prêt", 3000)
        print(f"DEBUG: on_engine_started terminé")
        
    def on_engine_stopped(self):
        """Handle engine stopped signal"""
        self.engine_panel.clear_engine_status()
    
    def on_avatar_started(self, avatar_name: str):
        """Handle avatar engine started signal"""
        print(f"DEBUG: MainWindow.on_avatar_started - Avatar {avatar_name} démarré")
        self.statusBar().showMessage(f"Avatar {avatar_name} prêt - À vous de jouer!", 3000)
    
    def on_avatar_stopped(self):
        """Handle avatar engine stopped signal"""
        print("DEBUG: MainWindow.on_avatar_stopped - Avatar arrêté")
        self.statusBar().showMessage("Avatar arrêté", 2000)
    
    def on_avatar_error(self, error_msg: str):
        """Handle avatar engine error"""
        print(f"ERROR: MainWindow.on_avatar_error - {error_msg}")
        QMessageBox.critical(self, "Erreur de l'avatar", error_msg)
    
    def on_avatar_move_ready(self, move):
        """Handle avatar move result (called from signal, thread-safe)"""
        print(f"DEBUG: on_avatar_move_ready appelé avec move={move}")
        
        if not move:
            self.chessboard.setEnabled(True)
            self.statusBar().showMessage("Erreur: l'avatar n'a pas pu jouer", 2000)
            return
        
        try:
            # Play the move on the board
            if self.game.make_move(move):
                # Update notation panel
                pgn_text = self.game.get_pgn_moves()
                self.notation_panel.update_moves(pgn_text)
                
                # Switch clock
                if self.clock_widget.timer.isActive():
                    self.clock_widget.switch_clock()
                
                # Play appropriate sound
                if self.game.board.is_capture(move):
                    self.sound_manager.play_capture()
                elif self.game.board.is_castling(move):
                    self.sound_manager.play_castle()
                elif self.game.board.is_check():
                    self.sound_manager.play_check()
                else:
                    self.sound_manager.play_move()
                
                # Update the board display
                self.chessboard.set_board(self.game.board)
                
                # Check game over
                if self.game.is_game_over():
                    result = self.game.get_result()
                    reason = self.get_game_over_reason()
                    self.statusBar().showMessage(f"Partie terminée - {result}")
                    self.notation_panel.set_game_info(f"Partie terminée - {result}")
                    self.sound_manager.play_game_end()
                    self.play_mode = "free"
                    self.playing_vs_avatar = False
                    # Show game over dialog
                    self.show_game_over_dialog(result, reason)
                else:
                    # Handle AI vs AI modes
                    if self.play_mode == "avatar_vs_avatar":
                        # Avatar vs Avatar: continue playing with alternating avatars
                        from PyQt6.QtCore import QTimer
                        QTimer.singleShot(800, lambda: self.auto_play_avatar_move())
                    elif self.play_mode == "avatar_vs_engine":
                        # Avatar vs Engine: engine plays next
                        if self.game.board.turn == chess.BLACK:
                            from PyQt6.QtCore import QTimer
                            QTimer.singleShot(800, lambda: self.request_engine_move())
                        else:
                            # Avatar plays next
                            from PyQt6.QtCore import QTimer
                            QTimer.singleShot(800, lambda: self.request_avatar_move())
                    else:
                        # Normal mode: Re-enable board interaction after avatar move
                        self.chessboard.setEnabled(True)
                        print(f"DEBUG: Échiquier réactivé, turn={self.game.board.turn}")
                        avatar = self.avatar_manager.get_avatar(self.avatar_id)
                        avatar_name = avatar.display_name if avatar else "Avatar"
                        self.statusBar().showMessage(f"{avatar_name} joue : {move.uci()} - À vous de jouer!", 3000)
        except Exception as e:
            print(f"ERROR: Avatar move failed: {e}")
            import traceback
            traceback.print_exc()
            self.statusBar().showMessage("Erreur de l'avatar", 3000)
            # Re-enable board on error
            self.chessboard.setEnabled(True)
        
    def on_engine_error(self, error_msg: str):
        """Handle engine error"""
        QMessageBox.critical(self, "Erreur du moteur", error_msg)
        self.engine_panel.clear_engine_status()
        
    def on_analysis_updated(self, data: dict):
        """Handle analysis update from engine"""
        self.engine_panel.update_analysis(data)
        
        # Update integrated evaluation bar on chessboard
        eval_cp = data.get('score_cp')
        mate_in = data.get('score_mate')
        self.chessboard.set_evaluation(eval_cp, mate_in)
        
    def on_engine_start_analysis(self):
        """Handle start analysis from engine panel"""
        print(f"DEBUG: on_engine_start_analysis - engine_running={self.engine_manager.is_engine_running()}")
        
        if not self.engine_manager.is_engine_running():
            QMessageBox.information(
                self,
                "Moteur non demarre",
                "Pour analyser, vous devez d'abord:\n\n"
                "1. Configurer un moteur:\n"
                "   Menu -> Moteur -> Configuration des moteurs...\n\n"
                "2. Demarrer le moteur:\n"
                "   Menu -> Moteur -> Demarrer le moteur (Ctrl+Shift+E)\n\n"
                "Astuce: L'application demarre automatiquement\n"
                "le premier moteur configure au lancement."
            )
            self.engine_panel._on_stop_clicked()
            return
        
        print("DEBUG: Appel de request_analysis()")
        self.request_analysis()
        
    def on_engine_stop_analysis(self):
        """Handle stop analysis from engine panel"""
        self.engine_manager.stop_analysis()
        
    def on_engine_option_changed(self, name: str, value: any):
        """Handle UCI option change from engine panel"""
        print(f"DEBUG: MainWindow.on_engine_option_changed {name}={value}")
        self.engine_manager.update_option(name, value)
        
    def request_analysis(self):
        """Request analysis of current position"""
        print(f"DEBUG: request_analysis - board FEN: {self.game.board.fen()}")
        self.engine_manager.analyze_position(
            self.game.board,
            multipv=3,  # Analyze top 3 moves
            time_limit=2.0  # 2 seconds per position
        )
        print("DEBUG: analyze_position appele")
        
    # Avatar methods
    def create_avatar(self):
        """Open avatar creation dialog"""
        dialog = AvatarCreationDialog(self.avatar_manager, self)
        dialog.avatar_created.connect(self.on_avatar_created)
        dialog.exec()
        
    def on_avatar_created(self, avatar_id: str):
        """Handle new avatar creation"""
        self.statusBar().showMessage(f"Avatar créé avec succès!", 3000)
        
    def manage_avatars(self):
        """Open avatar management panel in a dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton
        from ui.avatar_config_dialog import AvatarConfigDialog
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Gérer les Avatars")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        avatar_panel = AvatarPanel(self.avatar_manager)
        # When "Play" button is clicked, close this dialog and open NewGameDialog with avatar preselected
        avatar_panel.avatar_selected.connect(lambda aid: self._start_game_with_avatar(aid, dialog))
        avatar_panel.avatar_configure_requested.connect(lambda aid: self.configure_avatar(aid))
        avatar_panel.create_avatar_requested.connect(lambda: self.create_avatar())
        layout.addWidget(avatar_panel)
        
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        dialog.exec()
    
    def _start_game_with_avatar(self, avatar_id: str, manage_dialog):
        """Start a new game with a specific avatar (called from avatar panel)"""
        # Close the manage avatars dialog
        if manage_dialog:
            manage_dialog.accept()
        
        # Trigger new game which will open NewGameDialog
        # User can then select vs_avatar mode and choose this avatar
        self.new_game()
        # Note: Ideally we'd preselect the avatar in NewGameDialog, but that requires
        # passing avatar_id to NewGameDialog, which would require modifying its interface.
        # For now, user needs to manually select the avatar from the dropdown.
    
    def configure_avatar(self, avatar_id: str):
        """Open avatar configuration dialog"""
        from ui.avatar_config_dialog import AvatarConfigDialog
        
        avatar = self.avatar_manager.get_avatar(avatar_id)
        if not avatar:
            QMessageBox.warning(self, "Erreur", "Avatar non trouvé")
            return
        
        dialog = AvatarConfigDialog(avatar, self.avatar_manager, self)
        dialog.exec()
    
    # Note: L'ancien système d'avatar (start_avatar_game, start_avatar_game_async, make_avatar_move, etc.)
    # a été remplacé par le nouveau système utilisant AvatarEngineManager et intégré dans new_game()
    # avec le mode "vs_avatar". Ces méthodes ont été supprimées pour éviter les conflits.
    
    def open_board_config(self):
        """Open board configuration dialog"""
        dialog = BoardConfigDialog(self.board_config, self)
        dialog.config_changed.connect(self.on_board_config_changed)
        dialog.exec()
        
    def on_board_config_changed(self, config: dict):
        """Handle board configuration change"""
        self.apply_board_config()
        self.statusBar().showMessage("Configuration de l'échiquier mise à jour", 3000)
        
    def apply_board_config(self):
        """Apply board configuration to chessboard"""
        # Update colors
        from PyQt6.QtGui import QColor
        self.chessboard.light_square = QColor(self.board_config.get('light_square_color'))
        self.chessboard.dark_square = QColor(self.board_config.get('dark_square_color'))
        self.chessboard.highlight_color = QColor(self.board_config.get('highlight_color'))
        self.chessboard.selected_color = QColor(self.board_config.get('selected_color'))
        self.chessboard.legal_move_color = QColor(self.board_config.get('legal_move_color'))
        
        # Update square size
        square_size = self.board_config.get('square_size')
        self.chessboard.square_size = square_size
        self.chessboard.board_size = square_size * 8
        self.chessboard.setMinimumSize(self.chessboard.board_size + 60, self.chessboard.board_size + 60)
        
        # Update piece style (if needed for future ASCII implementation)
        # self.chessboard.piece_style = self.board_config.get('piece_style')
        
        # Update sound settings
        self.sound_manager.set_enabled(self.board_config.get('sounds_enabled'))
        self.sound_manager.set_volume(self.board_config.get('sound_volume'))
        
        # Redraw board
        self.chessboard.update()
    
    def get_game_over_reason(self) -> str:
        """Determine the reason for game over"""
        if self.game.board.is_checkmate():
            return "Échec et mat"
        elif self.game.board.is_stalemate():
            return "Pat"
        elif self.game.board.is_insufficient_material():
            return "Matériel insuffisant"
        elif self.game.board.is_fifty_moves():
            return "Règle des 50 coups"
        elif self.game.board.is_repetition():
            return "Répétition de position"
        else:
            return "Partie terminée"
    
    def show_game_over_dialog(self, result: str, reason: str):
        """Show game over dialog"""
        print(f"DEBUG: show_game_over_dialog appelé")
        print(f"DEBUG: result='{result}'")
        print(f"DEBUG: reason='{reason}'")
        
        # Stop the clock when game ends
        if self.clock_widget.timer.isActive():
            self.clock_widget.pause()
            print("DEBUG: Pendule arrêtée (partie terminée)")
        
        dialog = GameOverDialog(result, reason, self)
        dialog.new_game_requested.connect(self.new_game)
        dialog.exec()
    
    def on_time_expired(self, color: str):
        """Handle time expiration"""
        print(f"DEBUG: Temps écoulé pour {color}")
        if color == 'white':
            result = "0-1"
            reason = "Temps écoulé pour les Blancs"
        else:
            result = "1-0"
            reason = "Temps écoulé pour les Noirs"
        
        self.show_game_over_dialog(result, reason)
        self.statusBar().showMessage(f"Temps écoulé ! {reason}", 5000)
    
    def resign_game(self):
        """Handle resign button - player resigns"""
        if self.game.board.is_game_over():
            QMessageBox.information(self, "Partie terminée", "La partie est déjà terminée.")
            return
        
        # Confirm resignation
        reply = QMessageBox.question(
            self,
            "Confirmer l'abandon",
            "Êtes-vous sûr de vouloir abandonner cette partie ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Determine who resigned (opposite of who's turn it is wins)
            if self.game.board.turn == chess.WHITE:
                result = "0-1"  # White resigns, Black wins
                reason = "Abandon des Blancs"
            else:
                result = "1-0"  # Black resigns, White wins
                reason = "Abandon des Noirs"
            
            # Update game state
            self.statusBar().showMessage(f"Partie terminée - {reason}")
            self.notation_panel.set_game_info(f"{reason} - {result}")
            
            # Stop analysis and games
            if self.engine_manager.is_analyzing:
                self.engine_manager.stop_analysis()
            if self.playing_vs_avatar:
                self.playing_vs_avatar = False
            if self.play_mode == "vs_engine":
                self.play_mode = "free"
                self.waiting_for_engine = False
            
            # Show game over dialog
            self.show_game_over_dialog(result, reason)
    
    def offer_draw(self):
        """Handle draw offer button"""
        if self.game.board.is_game_over():
            QMessageBox.information(self, "Partie terminée", "La partie est déjà terminée.")
            return
        
        # Confirm draw offer
        message = "Voulez-vous proposer un match nul ?\n\n(En mode solo, cela accepte immédiatement la nulle)"
        if self.play_mode == "vs_engine":
            message = "Voulez-vous déclarer un match nul contre le moteur ?"
        
        reply = QMessageBox.question(
            self,
            "Proposer la nulle",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = "1/2-1/2"
            reason = "Nulle par accord mutuel"
            
            # Update game state
            self.statusBar().showMessage(f"Partie terminée - {reason}")
            self.notation_panel.set_game_info(f"{reason} - {result}")
            
            # Stop analysis and games
            if self.engine_manager.is_analyzing:
                self.engine_manager.stop_analysis()
            if self.playing_vs_avatar:
                self.playing_vs_avatar = False
            if self.play_mode == "vs_engine":
                self.play_mode = "free"
                self.waiting_for_engine = False
            
            # Show game over dialog
            self.show_game_over_dialog(result, reason)
    
    def flip_board_manual(self):
        """Manually flip the board"""
        self.chessboard.flip_board()
    
    def on_navigate_to_move(self, move_index: int):
        """
        Navigate to a specific move in the game history
        
        Args:
            move_index: Index of the move (0 = start position, 1 = after first move, etc.)
        """
        # Créer un board temporaire pour rejouer les coups
        temp_board = chess.Board()
        
        # Rejouer les coups jusqu'à l'index demandé
        if move_index > 0 and move_index <= len(self.game.board.move_stack):
            for i in range(move_index):
                temp_board.push(self.game.board.move_stack[i])
        
        # Afficher la position
        self.chessboard.set_board(temp_board)
        
        # Mettre à jour la barre de statut
        if move_index == 0:
            self.statusBar().showMessage("Position de départ")
        elif move_index == len(self.game.board.move_stack):
            self.statusBar().showMessage("Position actuelle")
        else:
            turn = "Blancs" if temp_board.turn == chess.WHITE else "Noirs"
            self.statusBar().showMessage(f"Après le coup {move_index} - Trait aux {turn}")
    
    def open_theme_config(self):
        """Open theme and piece set configuration dialog"""
        current_theme = self.chessboard.current_theme
        current_piece_set = self.chessboard.piece_set
        
        dialog = ThemeConfigDialog(self, current_theme, current_piece_set)
        dialog.theme_changed.connect(self.on_theme_changed)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            theme = dialog.get_selected_theme()
            piece_set = dialog.get_selected_piece_set()
            self.on_theme_changed(theme, piece_set)
            self.statusBar().showMessage(f"Thème appliqué: {theme} avec pièces {piece_set}", 3000)
    
    def on_theme_changed(self, theme_name: str, piece_set: str):
        """Handle theme and piece set changes"""
        self.chessboard.set_theme(theme_name)
        self.chessboard.set_piece_set(piece_set)
        self.statusBar().showMessage(f"Thème: {theme_name} | Pièces: {piece_set}", 2000)
    
    def apply_layout_preset(self, preset_name: str):
        """
        Apply a predefined layout preset
        
        Args:
            preset_name: Name of the preset to apply
        """
        preset = LayoutPresets.get_preset(preset_name)
        
        # Show/hide panels based on preset
        panels = preset.get("panels", {})
        
        if hasattr(self, 'engine_panel'):
            self.engine_panel.setVisible(panels.get("engine_panel", True))
        if hasattr(self, 'opening_panel'):
            self.opening_panel.setVisible(panels.get("opening_panel", True))
        if hasattr(self, 'notation_panel'):
            self.notation_panel.setVisible(panels.get("notation_panel", True))
        if hasattr(self, 'avatar_panel'):
            self.avatar_panel.setVisible(panels.get("avatar_panel", True))
        
        # Apply splitter sizes if available
        splitter_sizes = preset.get("splitter_sizes", {})
        
        if hasattr(self, 'main_splitter') and "main" in splitter_sizes:
            main_sizes = splitter_sizes["main"]
            total = sum(main_sizes)
            width = self.width()
            self.main_splitter.setSizes([int(width * s / total) for s in main_sizes])
        
        if hasattr(self, 'bottom_splitter') and "bottom" in splitter_sizes:
            bottom_sizes = splitter_sizes["bottom"]
            total = sum(bottom_sizes)
            if total > 0:
                width = self.bottom_splitter.width()
                self.bottom_splitter.setSizes([int(width * s / total) for s in bottom_sizes])
        
        if hasattr(self, 'right_splitter') and "right" in splitter_sizes:
            right_sizes = splitter_sizes["right"]
            total = sum(right_sizes)
            if total > 0:
                height = self.right_splitter.height()
                self.right_splitter.setSizes([int(height * s / total) for s in right_sizes])
        
        self.statusBar().showMessage(f"Disposition '{preset['name']}' appliquée", 3000)
    
    def show_game_report(self):
        """Show detailed game report dialog"""
        dialog = GameReportDialog(self.game, self)
        dialog.exec()
    
    def show_about(self):
        """Show about dialog"""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def _save_window_state(self):
        """Save window state (dock positions, sizes, etc.)"""
        import json
        state = {
            'geometry': self.saveGeometry().toBase64().data().decode('utf-8'),
            'window_state': self.saveState().toBase64().data().decode('utf-8')
        }
        
        try:
            with open('window_state.json', 'w') as f:
                json.dump(state, f)
            self.statusBar().showMessage("Disposition sauvegardée !", 2000)
        except Exception as e:
            print(f"Error saving window state: {e}")
    
    def _restore_window_state(self):
        """Restore window state from saved file"""
        import json
        import os
        
        if not os.path.exists('window_state.json'):
            return
        
        try:
            with open('window_state.json', 'r') as f:
                state = json.load(f)
            
            from PyQt6.QtCore import QByteArray
            import base64
            
            geometry = QByteArray.fromBase64(state['geometry'].encode('utf-8'))
            window_state = QByteArray.fromBase64(state['window_state'].encode('utf-8'))
            
            self.restoreGeometry(geometry)
            self.restoreState(window_state)
        except Exception as e:
            print(f"Error restoring window state: {e}")
    
    def _reset_layout(self):
        """Reset to default layout"""
        # Remove saved state
        import os
        if os.path.exists('window_state.json'):
            os.remove('window_state.json')
        
        # Reset all docks
        self.engine_dock.setFloating(False)
        self.opening_dock.setFloating(False)
        self.notation_dock.setFloating(False)
        self.avatar_dock.setFloating(False)
        self.clock_dock.setFloating(False)
        self.controls_dock.setFloating(False)
        
        # Re-add to default positions
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.engine_dock)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.opening_dock)
        self.tabifyDockWidget(self.engine_dock, self.opening_dock)
        
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.avatar_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.notation_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.clock_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.controls_dock)
        
        self.engine_dock.raise_()
        self.statusBar().showMessage("Disposition réinitialisée !", 2000)
    
    def closeEvent(self, event):
        """Handle window close event"""
        print("DEBUG: MainWindow.closeEvent appelé")
        
        # Auto-save window state
        self._save_window_state()
        
        # Stop avatar engine if running
        if self.avatar_engine_manager.is_avatar_running():
            print("DEBUG: Arrêt de l'avatar engine")
            self.avatar_engine_manager.stop_avatar()
        
        # Stop main engine if running
        if self.engine_manager.is_engine_running():
            print("DEBUG: Arrêt du moteur principal")
            self.engine_manager.stop_engine()
        
        # Accept the close event
        event.accept()
        print("DEBUG: Fenêtre fermée proprement")

