# ChessAvatar - Quick Start Guide

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
python main.py
```

## Features Implemented (Phase 1)

### ✅ Main Window Architecture
- Modern dark-themed interface inspired by Fritz 20
- Responsive layout with resizable panels
- Professional menu bar with keyboard shortcuts

### ✅ Menu System
- **Fichier (File)**: Nouvelle partie, Ouvrir/Sauvegarder PGN, Quitter
- **Échiquier (Board)**: Retourner l'échiquier, Copier/Coller FEN
- **Analyse (Analysis)**: Annuler le coup, Afficher les coups légaux
- **Moteur (Engine)**: Configuration et analyse (placeholders pour futures phases)

### ✅ 2D Chessboard
- Interactive drag-and-drop piece movement
- Visual feedback for selected pieces and legal moves
- Board coordinates (files a-h, ranks 1-8)
- Board flip functionality
- High-contrast piece rendering with Unicode symbols

### ✅ Right Panel
- **PGN Notation Display**: Shows all moves in standard notation
- **Chess Clock**: Dual timer with start/pause/reset controls
- Auto-switching clocks after each move
- Visual highlighting of active clock

### ✅ Game Logic
- Full chess rules implementation via python-chess library
- Legal move validation
- Game state detection (checkmate, stalemate, draws)
- Move history tracking
- Undo functionality

### ✅ Modern Dark Theme
- Professional color scheme
- Consistent styling across all components
- High readability
- Optimized for extended use

## Keyboard Shortcuts

- `Ctrl+N` - New game
- `Ctrl+O` - Open PGN
- `Ctrl+S` - Save PGN
- `Ctrl+Q` - Quit
- `Ctrl+F` - Flip board
- `Ctrl+Z` - Undo move
- `Ctrl+Shift+C` - Copy FEN
- `Ctrl+Shift+V` - Paste FEN
- `Ctrl+E` - Start analysis

## How to Play

1. Click and drag pieces to move them
2. Legal moves are highlighted when you select a piece
3. The notation panel updates automatically
4. Use the clock to track time (optional)
5. Use Ctrl+Z to undo moves

## Project Structure

```
chessavatar-project/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── core/
│   ├── __init__.py
│   └── game.py                # Chess game logic wrapper
└── ui/
    ├── __init__.py
    ├── main_window.py         # Main application window
    ├── chessboard.py          # Interactive chessboard widget
    ├── notation_panel.py      # PGN notation display
    ├── clock_widget.py        # Chess timer
    └── styles.py              # Dark theme styling
```

## Next Phases (Coming Soon)

- **Phase 2**: Engine integration (Stockfish)
- **Phase 3**: Position analysis and evaluation
- **Phase 4**: Database and opening book
- **Phase 5**: Microsoft Store optimization

## Technical Details

- **Framework**: PyQt6
- **Chess Logic**: python-chess library
- **Platform**: Windows (with Microsoft Store optimization planned)
- **Python Version**: 3.8+

## Troubleshooting

If you encounter any issues:

1. Ensure Python 3.8+ is installed
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Check that PyQt6 is properly installed: `python -c "from PyQt6 import QtWidgets"`

## Development Notes

The application follows a clean architecture:
- **UI Layer**: PyQt6 widgets and windows
- **Core Layer**: Chess logic and game state management
- **Separation of Concerns**: Each component has a single responsibility

The codebase is ready for future enhancements including:
- UCI chess engine integration
- Advanced analysis features
- Position database
- Opening preparation tools

