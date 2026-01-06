# ChessAvatar - Build & Deployment Guide

## 📦 Phase 5: Microsoft Store Preparation

This guide covers building and deploying ChessAvatar as a Windows application ready for Microsoft Store submission.

---

## 🛠️ Build Options

ChessAvatar provides **three build methods**:

### 1. **PyInstaller** (Recommended for Quick Builds)
- ✅ Fast compilation (~5 minutes)
- ✅ Easy to use
- ✅ Well-tested
- ⚠️ Larger file size (~80-120 MB)

### 2. **Nuitka** (Recommended for Performance)
- ✅ Native C code compilation
- ✅ Faster execution
- ✅ Smaller file size (~50-80 MB)
- ⚠️ Longer compilation (~10-30 minutes)
- ⚠️ Requires C compiler (MinGW or Visual Studio)

### 3. **MSIX Package** (For Microsoft Store)
- ✅ Store-ready format
- ✅ Automatic updates
- ✅ Trusted installation
- ⚠️ Requires Windows SDK

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **All dependencies** installed:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller nuitka Pillow
   ```

3. **Windows SDK** (for MSIX builds):
   - Download: https://developer.microsoft.com/windows/downloads/windows-sdk/
   - Required tools: `makeappx.exe`, `signtool.exe`

4. **C Compiler** (for Nuitka):
   - MinGW-w64: https://winlibs.com/
   - OR Visual Studio: https://visualstudio.microsoft.com/

---

## 📋 Build Steps

### Method 1: PyInstaller Build

```bash
# 1. Run PyInstaller build script
python build_pyinstaller.py

# 2. Test the executable
cd dist\ChessAvatar
ChessAvatar.exe

# 3. ZIP package is created automatically
# Output: dist\ChessAvatar-1.0.0-Windows.zip
```

**What it does:**
1. ✅ Checks all dependencies
2. ✅ Creates version info
3. ✅ Bundles Python + dependencies
4. ✅ Embeds resources (icon, sounds)
5. ✅ Creates standalone executable
6. ✅ Generates distribution package

**Output Structure:**
```
dist/
└── ChessAvatar/
    ├── ChessAvatar.exe          # Main executable
    ├── _internal/               # Dependencies
    ├── sounds/                  # Sound files
    ├── README.txt
    └── LICENSE.txt
```

---

### Method 2: Nuitka Build

```bash
# 1. Run Nuitka build script
python build_nuitka.py

# This will take 10-30 minutes depending on your PC

# 2. Test the executable
cd dist\ChessAvatar_Nuitka
ChessAvatar.exe

# 3. ZIP package is created automatically
# Output: dist\ChessAvatar-1.0.0-Windows-Nuitka.zip
```

**What it does:**
1. ✅ Compiles Python → C code
2. ✅ Applies Link Time Optimization (LTO)
3. ✅ Creates native executable
4. ✅ Smaller & faster than PyInstaller

**Performance Comparison:**
| Metric | PyInstaller | Nuitka |
|--------|-------------|--------|
| Build Time | 5 min | 20 min |
| File Size | 100 MB | 60 MB |
| Startup Time | 3s | 1s |
| Performance | Good | Excellent |

---

### Method 3: MSIX Package (Microsoft Store)

```bash
# 1. First, build with PyInstaller
python build_pyinstaller.py

# 2. Create MSIX package
python build_msix.py

# Output: ChessAvatar-1.0.0.0.msix
```

**What it does:**
1. ✅ Creates app assets (icons, tiles, splash screen)
2. ✅ Prepares MSIX directory structure
3. ✅ Generates AppxManifest.xml
4. ✅ Packages with `makeappx.exe`
5. ✅ Creates submission package

**Output:**
```
ChessAvatar-1.0.0.0.msix        # MSIX package
store_submission/                # Ready for submission
├── ChessAvatar-1.0.0.0.msix
└── SUBMISSION_NOTES.txt
```

---

## 🎨 Customization

### Update Version

Edit `version.py`:
```python
__version__ = "1.1.0"
VERSION_MAJOR = 1
VERSION_MINOR = 1
VERSION_PATCH = 0
```

Then rebuild.

### Replace Icon

1. Create `resources/icon.ico` (256x256, ICO format)
2. Rebuild

**Tools for creating icons:**
- IcoFX: https://icofx.ro/
- Online: https://convertico.com/

### Replace App Assets (for MSIX)

Replace placeholder images in `msix_build/Assets/`:
- `Square44x44Logo.png` (44×44)
- `Square71x71Logo.png` (71×71)
- `Square150x150Logo.png` (150×150)
- `Square310x310Logo.png` (310×310)
- `Wide310x150Logo.png` (310×150)
- `StoreLogo.png` (50×50)
- `SplashScreen.png` (620×300)

**Requirements:**
- PNG format
- Exact dimensions
- Transparent background recommended
- Follow Microsoft design guidelines

---

## 🧪 Testing

### Test Standalone Executable

```bash
# PyInstaller build
cd dist\ChessAvatar
ChessAvatar.exe

# Nuitka build
cd dist\ChessAvatar_Nuitka
ChessAvatar.exe
```

**Test checklist:**
- ✅ Application starts
- ✅ Main window displays correctly
- ✅ Chessboard renders
- ✅ Menus work
- ✅ Can move pieces
- ✅ Engine configuration works
- ✅ Avatar creation works
- ✅ PGN import/export works
- ✅ Sounds play correctly

### Test MSIX Package

```powershell
# Install package (requires developer mode)
Add-AppxPackage .\ChessAvatar-1.0.0.0.msix

# Launch
Start-Process "chessavatar:launch"

# Or find in Start Menu

# Uninstall
Get-AppxPackage *ChessAvatar* | Remove-AppxPackage
```

---

## 📤 Microsoft Store Submission

### Step 1: Prepare Package

```bash
# Build MSIX
python build_pyinstaller.py
python build_msix.py
```

### Step 2: Sign Package

You need a **Store certificate** from Microsoft Partner Center.

```powershell
# Sign with certificate
signtool sign /fd SHA256 /a /f YourCertificate.pfx `
    /p YourPassword ChessAvatar-1.0.0.0.msix
```

### Step 3: Test on Clean Windows

Test on Windows 10/11 VM:
1. Install MSIX
2. Launch application
3. Test all features
4. Check performance
5. Uninstall cleanly

### Step 4: Partner Center Submission

1. **Register**: https://partner.microsoft.com/dashboard
2. **Create App**: Reserve app name "ChessAvatar"
3. **Upload Package**: `ChessAvatar-1.0.0.0.msix`
4. **App Listing**:
   - **Description**: Write compelling description
   - **Screenshots**: 1-10 images (1366×768 or higher)
   - **Features**: List key features
   - **Category**: Games → Board
   - **Age Rating**: PEGI 3 / ESRB Everyone

5. **Pricing**: Free or Paid
6. **Submit for Review**: 24-48 hours

---

## 📊 Build Comparison

| Feature | PyInstaller | Nuitka | MSIX |
|---------|-------------|--------|------|
| **Build Time** | 5 min | 20 min | 10 min* |
| **File Size** | ~100 MB | ~60 MB | ~100 MB |
| **Performance** | Good | Excellent | Good |
| **Compatibility** | Win 7+ | Win 7+ | Win 10+ |
| **Auto-Update** | ❌ | ❌ | ✅ |
| **Store Distribution** | ❌ | ❌ | ✅ |
| **Trusted Installer** | ⚠️ | ⚠️ | ✅ |

*After PyInstaller build

---

## 🐛 Troubleshooting

### PyInstaller Issues

**Problem**: "Failed to execute script"
```bash
# Run with console to see errors
pyinstaller chessavatar.spec --console
```

**Problem**: Missing modules
```bash
# Add to hiddenimports in chessavatar.spec
hiddenimports=['missing_module']
```

### Nuitka Issues

**Problem**: C compiler not found
```bash
# Install MinGW-w64
# Add to PATH: C:\mingw64\bin
```

**Problem**: Out of memory
```bash
# Add --lto=no to disable LTO
# Or increase virtual memory
```

### MSIX Issues

**Problem**: makeappx not found
```powershell
# Add Windows SDK to PATH
$env:Path += ";C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64"
```

**Problem**: Invalid manifest
```bash
# Validate manifest
makeappx.exe validate /file ChessAvatar-1.0.0.0.msix
```

### Runtime Issues

**Problem**: DLL not found
- Include missing DLL in binaries
- Or install Visual C++ Redistributable

**Problem**: Sounds don't play
- Check `sounds/` folder is included
- Verify file paths in code

---

## 📁 Project Structure After Build

```
chessavatar-project/
├── main.py                          # Entry point
├── version.py                       # Version info
├── requirements.txt                 # Dependencies
├── chessavatar.spec                # PyInstaller spec
├── build_pyinstaller.py            # PyInstaller build script
├── build_nuitka.py                 # Nuitka build script
├── build_msix.py                   # MSIX build script
├── AppxManifest.xml                # Store manifest
├── version_info.txt                # Windows version info
│
├── resources/
│   └── icon.ico                    # App icon
│
├── sounds/                         # Sound files
│   ├── move.wav
│   ├── capture.wav
│   └── check.wav
│
├── dist/                           # Build outputs
│   ├── ChessAvatar/               # PyInstaller output
│   ├── ChessAvatar_Nuitka/        # Nuitka output
│   ├── ChessAvatar-1.0.0-Windows.zip
│   └── ChessAvatar-1.0.0-Windows-Nuitka.zip
│
├── msix_build/                     # MSIX staging
│   ├── ChessAvatar.exe
│   ├── AppxManifest.xml
│   └── Assets/                     # Store assets
│
├── store_submission/               # Ready for Store
│   ├── ChessAvatar-1.0.0.0.msix
│   └── SUBMISSION_NOTES.txt
│
└── build/                          # Temporary build files
```

---

## ✅ Pre-Submission Checklist

### Technical
- [ ] Builds successfully with PyInstaller
- [ ] Builds successfully with Nuitka
- [ ] MSIX package created
- [ ] Application launches without errors
- [ ] All features tested and working
- [ ] No crashes or freezes
- [ ] Performance is acceptable
- [ ] File size is reasonable (<200 MB)

### Assets
- [ ] Icon created (256×256 ICO)
- [ ] Store logo (50×50 PNG)
- [ ] Tiles created (44×44, 71×71, 150×150, 310×310)
- [ ] Wide tile (310×150 PNG)
- [ ] Splash screen (620×300 PNG)
- [ ] Screenshots (3-10 images, 1366×768+)

### Documentation
- [ ] README.txt included
- [ ] LICENSE.txt included
- [ ] Version info correct
- [ ] Copyright notices updated
- [ ] Store description written
- [ ] Feature list prepared
- [ ] Age rating determined

### Legal
- [ ] Partner Center account created
- [ ] App name reserved
- [ ] Privacy policy prepared (if collecting data)
- [ ] Terms of service prepared (if needed)
- [ ] Certificates obtained

---

## 🎯 Next Steps After Submission

1. **Monitor Certification**: 24-48 hours
2. **Address Feedback**: Fix any issues reported
3. **Publish**: Once approved
4. **Marketing**: Promote your app
5. **Updates**: Plan version 1.1 with new features

---

## 📞 Support

- **Build Issues**: Check troubleshooting section
- **Store Issues**: Microsoft Partner Center support
- **App Issues**: GitHub Issues

---

## 📄 Additional Resources

- **PyInstaller**: https://pyinstaller.org/
- **Nuitka**: https://nuitka.net/
- **Windows SDK**: https://developer.microsoft.com/windows/downloads/
- **Partner Center**: https://partner.microsoft.com/dashboard
- **Store Guidelines**: https://docs.microsoft.com/windows/uwp/publish/

---

**Built with ❤️ for Windows**

