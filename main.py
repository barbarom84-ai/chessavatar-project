"""
ChessAvatar - Advanced Chess Application
Main entry point
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
from debug_logger import init_debug_logger, log_info, log_error, log_exception


def main():
    """Main application entry point"""
    # Initialiser le système de debug
    logger = init_debug_logger()
    
    try:
        logger.log_app_start()
        log_info("Initialisation de l'application...")
        
        app = QApplication(sys.argv)
        
        # Note: HiDPI support is automatically enabled in Qt6
        # AA_EnableHighDpiScaling and AA_UseHighDpiPixmaps are deprecated in Qt6
        log_info("HiDPI support: Activé automatiquement (Qt6)")
        
        # Set application metadata
        app.setApplicationName("ChessAvatar")
        app.setOrganizationName("ChessAvatar")
        app.setApplicationVersion("1.0.0")
        log_info("Métadonnées application configurées")
        
        # Set default font
        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        app.setFont(font)
        log_info("Police par défaut: Segoe UI 10pt")
        
        # Initialize resolution manager and log info
        from ui.resolution_manager import get_resolution_manager
        res_mgr = get_resolution_manager()
        log_info(f"Résolution écran: {res_mgr.screen_size.width()}x{res_mgr.screen_size.height()}")
        log_info(f"DPI: {res_mgr.screen_dpi}")
        log_info(f"Facteur d'échelle: {res_mgr.scale_factor:.2f}")
        log_info(f"Taille échiquier optimale: {res_mgr.get_board_size()}px")
        
        # Create and show main window
        log_info("Création de la fenêtre principale...")
        window = MainWindow()
        window.show()
        log_info("Application démarrée avec succès!")
        
        # Run application
        exit_code = app.exec()
        
        logger.log_app_stop()
        sys.exit(exit_code)
        
    except Exception as e:
        log_exception("Erreur fatale lors du démarrage")
        log_error(f"Détails de l'erreur: {str(e)}")
        raise


if __name__ == "__main__":
    main()

