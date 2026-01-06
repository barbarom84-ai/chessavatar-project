"""
ChessAvatar - Debug Logger
Système de logging et gestion des crashs
"""

import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path
import json


class DebugLogger:
    """Gestionnaire de logs et crashs pour ChessAvatar"""
    
    def __init__(self, log_dir="logs"):
        """Initialise le système de logging"""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Nom du fichier de log avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"chessavatar_{timestamp}.log"
        self.crash_file = self.log_dir / f"crash_{timestamp}.json"
        
        # Configuration du logger
        self.logger = self._setup_logger()
        
        # Installer le gestionnaire d'exceptions global
        sys.excepthook = self.handle_exception
    
    def _setup_logger(self):
        """Configure le système de logging"""
        logger = logging.getLogger('ChessAvatar')
        logger.setLevel(logging.DEBUG)
        
        # Handler pour fichier (DEBUG et plus)
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Handler pour console (INFO et plus)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log(self, level, message, **kwargs):
        """Log un message avec données additionnelles"""
        if kwargs:
            message = f"{message} | Data: {json.dumps(kwargs, default=str)}"
        
        if level == 'debug':
            self.logger.debug(message)
        elif level == 'info':
            self.logger.info(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'critical':
            self.logger.critical(message)
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Gestionnaire global d'exceptions"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Permettre Ctrl+C de fonctionner normalement
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Logger l'exception
        self.logger.critical("CRASH DETECTE!", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Créer un rapport de crash détaillé
        crash_report = self._create_crash_report(exc_type, exc_value, exc_traceback)
        
        # Sauvegarder le rapport
        with open(self.crash_file, 'w', encoding='utf-8') as f:
            json.dump(crash_report, f, indent=2, default=str)
        
        print(f"\n{'='*60}")
        print("[X] CHESSAVATAR A CRASHE")
        print(f"{'='*60}")
        print(f"Un rapport de crash a ete cree: {self.crash_file}")
        print(f"Log complet disponible dans: {self.log_file}")
        print(f"{'='*60}\n")
        
        # Afficher l'erreur
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    
    def _create_crash_report(self, exc_type, exc_value, exc_traceback):
        """Crée un rapport de crash détaillé"""
        import platform
        
        # Extraire la stack trace
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "application": "ChessAvatar",
            "version": "1.0.0",
            "error": {
                "type": exc_type.__name__,
                "message": str(exc_value),
                "traceback": tb_lines
            },
            "system": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "architecture": platform.machine(),
                "processor": platform.processor()
            },
            "environment": {
                "cwd": str(Path.cwd()),
                "python_path": sys.executable
            }
        }
        
        # Ajouter les modules installés
        try:
            import pkg_resources
            installed_packages = {
                pkg.key: pkg.version 
                for pkg in pkg_resources.working_set
            }
            report["installed_packages"] = installed_packages
        except:
            pass
        
        return report
    
    def log_app_start(self):
        """Log le démarrage de l'application"""
        import platform
        
        self.logger.info("="*60)
        self.logger.info("DÉMARRAGE DE CHESSAVATAR")
        self.logger.info("="*60)
        self.logger.info(f"Version: 1.0.0")
        self.logger.info(f"Python: {platform.python_version()}")
        self.logger.info(f"Plateforme: {platform.platform()}")
        self.logger.info(f"Répertoire: {Path.cwd()}")
        self.logger.info("="*60)
    
    def log_app_stop(self):
        """Log l'arrêt normal de l'application"""
        self.logger.info("="*60)
        self.logger.info("ARRÊT NORMAL DE CHESSAVATAR")
        self.logger.info("="*60)
    
    def log_move(self, move, board_fen=None):
        """Log un coup d'échecs"""
        if board_fen:
            self.logger.debug(f"Move: {move} | FEN: {board_fen}")
        else:
            self.logger.debug(f"Move: {move}")
    
    def log_engine_event(self, event_type, **data):
        """Log un événement du moteur"""
        if data:
            data_str = " | ".join(f"{k}={v}" for k, v in data.items())
            self.logger.debug(f"Engine event: {event_type} | {data_str}")
        else:
            self.logger.debug(f"Engine event: {event_type}")
    
    def log_avatar_event(self, event_type, **data):
        """Log un événement d'avatar"""
        if data:
            data_str = " | ".join(f"{k}={v}" for k, v in data.items())
            self.logger.info(f"Avatar event: {event_type} | {data_str}")
        else:
            self.logger.info(f"Avatar event: {event_type}")
    
    def log_error_safe(self, context, error):
        """Log une erreur sans crasher"""
        try:
            self.logger.error(f"{context}: {str(error)}", exc_info=True)
        except Exception as e:
            # Fallback ultime
            print(f"ERROR in {context}: {error}")
            print(f"Logging error: {e}")


# Instance globale
debug_logger = None


def init_debug_logger(log_dir="logs"):
    """Initialise le logger global"""
    global debug_logger
    if debug_logger is None:
        debug_logger = DebugLogger(log_dir)
    return debug_logger


def get_logger():
    """Obtient le logger global"""
    global debug_logger
    if debug_logger is None:
        debug_logger = init_debug_logger()
    return debug_logger


# Fonctions utilitaires
def log_debug(message, **kwargs):
    """Log niveau DEBUG"""
    get_logger().log('debug', message, **kwargs)


def log_info(message, **kwargs):
    """Log niveau INFO"""
    get_logger().log('info', message, **kwargs)


def log_warning(message, **kwargs):
    """Log niveau WARNING"""
    get_logger().log('warning', message, **kwargs)


def log_error(message, **kwargs):
    """Log niveau ERROR"""
    get_logger().log('error', message, **kwargs)


def log_critical(message, **kwargs):
    """Log niveau CRITICAL"""
    get_logger().log('critical', message, **kwargs)


def log_exception(context):
    """Log l'exception courante"""
    get_logger().logger.exception(context)

