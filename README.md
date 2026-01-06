# ChessAvatar - Advanced Chess Application

A modern chess application inspired by Fritz 20, built with Python and PyQt6.

## ✨ Features

### Phase 1: Core Application ✅
- ✅ Modern dark-themed interface
- ✅ 2D chessboard with drag-and-drop piece movement
- ✅ PGN notation display in real-time
- ✅ Chess clock/timer with auto-switching

### Phase 2: Engine Integration ✅
- ✅ **UCI Chess engine integration** (Stockfish, Komodo, etc.)
- ✅ **Real-time position analysis** with evaluation bar
- ✅ **Multi-PV analysis** (best lines display)
- ✅ Engine configuration and management

### Phase 3: AI Avatar System ✅ **[UNIQUE FEATURE]**
- ✅ **Create AI avatars** from real players (Lichess/Chess.com)
- ✅ **Analyze 100 games** automatically
- ✅ **Reproduce playing style** (aggressive/positional/tactical)
- ✅ **Custom Stockfish configuration** per avatar
- ✅ **Profile photos** and complete statistics
- ✅ **Play against AI replicas** of real players

### Phase 4: Interactive Board & PGN ✅
- ✅ **Sound effects** (move, capture, check, castle, game end)
- ✅ **PGN import/export** with full metadata
- ✅ **Board customization** (colors, piece styles, themes)
- ✅ **Configuration persistence** with 3 preset themes

## Requirements

- Python 3.8 or higher
- PyQt6
- python-chess
- requests
- numpy

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## 🤖 AI Avatar System (Unique Feature!)

Create AI opponents that play like real players:

1. **Menu → Avatar → Create AI Avatar**
2. Enter a Lichess or Chess.com username
3. Fetch and analyze 100 games
4. Get complete style profile (openings, win rate, aggressive score)
5. **Play against the AI replica!**

The AI will:
- Play at the exact Elo level
- Use favorite openings
- Make human-like mistakes
- Reproduce the player's style

### Example: Create Magnus Carlsen AI

```
Username: DrNykterstein (Lichess)
→ 100 games analyzed
→ Elo: 3200+, Level: 20/20
→ Style: Positional (35/100 aggressive)
→ Openings: Ruy Lopez, Queen's Gambit
```

Now you can play against Magnus's AI!

## 🎨 Customization

**Board Configuration:**
- Menu → File → Board Configuration
- Choose colors for light/dark squares
- Select from 3 preset themes (Classic, Blue, Green)
- Adjust square size (50-120px)
- Enable/disable sounds and set volume

**Sound System:**
- Automatic sound effects for moves
- Different sounds for: normal move, capture, check, castle, game end
- Volume control (0-100%)

## 📖 PGN Support

**Import:**
- Menu → File → Open PGN (Ctrl+O)
- Load any standard PGN file
- Automatic board replay
- View game information

**Export:**
- Menu → File → Save PGN (Ctrl+S)
- Save current game with metadata
- Standard PGN format

## 🎯 Key Features Comparison

| Feature | ChessAvatar | Other Apps |
|---------|-------------|------------|
| UCI Engine Support | ✅ | ✅ |
| Position Analysis | ✅ | ✅ |
| Multi-PV | ✅ | ✅ |
| **AI Avatar from Real Players** | ✅ | ❌ |
| **Style Analysis** | ✅ | ❌ |
| **Custom Avatar Collection** | ✅ | ❌ |
| Board Customization | ✅ | ✅ |
| Sound Effects | ✅ | ✅ |
| PGN Import/Export | ✅ | ✅ |

**→ AI Avatar System makes ChessAvatar UNIQUE!**

## 🚀 Quick Start

1. **Configure Stockfish:**
   - Download from: https://stockfishchess.org/download/
   - Menu → Engine → Configure Engines
   - Add stockfish.exe

2. **Create Your First Avatar:**
   - Menu → Avatar → Create AI Avatar (Ctrl+Shift+A)
   - Platform: Lichess or Chess.com
   - Enter a username (e.g., "Hikaru", "GothamChess")
   - Wait for analysis
   - Upload a photo (optional)
   - Create!

3. **Play Against Avatar:**
   - Menu → Avatar → Manage Avatars
   - Select an avatar
   - Click "Play"
   - Enjoy!

## 📁 Project Structure

```
chessavatar-project/
├── main.py                         # Application entry point
├── version.py                      # Version management
├── debug_logger.py                 # Crash reporting system
├── core/                           # Business logic
│   ├── game.py                    # Chess game logic
│   ├── engine_manager.py          # UCI engine manager (async)
│   ├── api_service.py             # Lichess/Chess.com API
│   ├── style_analyzer.py          # Playing style analysis
│   ├── avatar_worker.py           # AI avatar engine (async)
│   ├── avatar_manager.py          # Avatar storage
│   ├── sound_manager.py           # Sound effects
│   └── pgn_manager.py             # PGN import/export
├── ui/                            # User interface
│   ├── main_window.py            # Main application window
│   ├── chessboard.py             # Interactive chessboard
│   ├── notation_panel.py         # PGN notation display
│   ├── clock_widget.py           # Chess clock with time controls
│   ├── engine_panel.py           # Engine analysis panel
│   ├── engine_config_dialog.py   # Engine configuration
│   ├── avatar_panel.py           # Avatar management
│   ├── avatar_creation_dialog.py # Avatar creation
│   ├── avatar_config_dialog.py   # Avatar customization
│   ├── board_config_dialog.py    # Board customization
│   ├── new_game_dialog.py        # New game setup
│   ├── game_over_dialog.py       # Game over dialog
│   ├── resolution_manager.py     # HiDPI/4K support
│   └── styles.py                 # Dark theme
├── docs/                          # Documentation
│   ├── QUICKSTART.md             # Quick start guide
│   ├── BUILD_GUIDE.md            # Build & deployment
│   ├── ENGINE_GUIDE.md           # Engine configuration
│   ├── AVATAR_SYSTEM_GUIDE.md    # Avatar system
│   ├── AVATAR_USER_GUIDE.md      # Avatar usage
│   ├── DEBUG_GUIDE.md            # Debugging
│   ├── QUICK_REFERENCE.md        # Keyboard shortcuts
│   └── MICROSOFT_STORE_SUCCESS.md # Store submission
├── sounds/                        # Sound effects
│   ├── move.wav, capture.wav, check.wav
│   ├── castle.wav, game_end.wav
├── avatars/                       # Avatar storage
│   ├── cache/                    # Game data cache
│   └── photos/                   # Avatar photos
├── logs/                          # Crash reports
├── build_store_ready.py           # Complete build script
├── sign_package.ps1               # Package signing (PowerShell)
├── AppxManifest.xml              # Microsoft Store manifest
└── requirements.txt               # Python dependencies
```

## 📊 Statistics

- **Total Code:** ~10,000+ lines
- **Classes:** 30+
- **Features:** 50+
- **Supported Engines:** All UCI engines
- **Supported Platforms:** Lichess, Chess.com
- **Sound Effects:** 5 types
- **Time Controls:** 13 presets (Bullet, Blitz, Rapid, Classical)
- **Board Themes:** 3 presets + custom
- **Documentation:** 8 comprehensive guides

## 🎓 Recommended Engines

### Free Engines
- **Stockfish** - Strongest free engine (3500+ Elo)
- **Leela Chess Zero** - Neural network based
- **Ethereal** - Strong and fast

### Commercial Engines
- **Komodo** - Positional style
- **Houdini** - Tactical style

## 📚 Documentation

All documentation is in the `docs/` folder:

### User Guides
- `README.md` - This file (overview)
- `docs/QUICKSTART.md` - Quick start guide
- `docs/ENGINE_GUIDE.md` - Engine configuration guide
- `docs/AVATAR_USER_GUIDE.md` - Avatar usage tutorial
- `docs/QUICK_REFERENCE.md` - Keyboard shortcuts & tips

### Build & Deployment
- `docs/BUILD_GUIDE.md` - Building executables and MSIX packages
- `docs/MICROSOFT_STORE_SUCCESS.md` - Store submission guide

### Technical Documentation
- `docs/AVATAR_SYSTEM_GUIDE.md` - AI Avatar system architecture
- `docs/DEBUG_GUIDE.md` - Debugging and crash reporting

## 🎉 What Makes ChessAvatar Special

1. **AI Avatar System** - Play against AI that mimics real players
2. **Style Analysis** - Understand playing styles (aggressive/tactical/positional)
3. **Professional UI** - Fritz 20-inspired dark theme
4. **Complete Solution** - Analysis + Training + Fun
5. **Open Source** - Extensible and customizable

## 🏆 Use Cases

### Training
- Play against avatars at your level
- Variety of playing styles
- Learn from mistakes

### Preparation
- Create avatar of your next opponent
- Study their opening repertoire
- Practice against their style

### Fun
- Create avatars of famous players
- Challenge your friends' avatars
- Collect a personal AI opponent library

### Analysis
- Deep position analysis with Stockfish
- Multi-PV to see alternatives
- PGN import for game review

## 📦 Building for Distribution

### Complete Build (Recommended)
```bash
python build_store_ready.py
```
Creates a complete, signed MSIX package ready for Microsoft Store submission.

### Package Signing
```powershell
.\sign_package.ps1
```
Signs the MSIX package with your developer certificate.

See `docs/BUILD_GUIDE.md` for detailed instructions.

## 🔮 Future Enhancements

Phase 6+ ideas:
- Opening book database
- Tactics trainer
- Endgame tablebase
- Online play
- Tournament mode
- More board themes

## 📝 License

MIT License

## 🙏 Credits

- **PyQt6** - Qt framework for Python
- **python-chess** - Chess logic and UCI protocol
- **Lichess & Chess.com** - Public APIs for game data
- **Stockfish** - Chess engine

---

**ChessAvatar - The chess app that learns from your opponents** 🚀♔♕♖♗♘♙

