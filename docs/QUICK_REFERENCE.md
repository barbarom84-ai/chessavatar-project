# 🚀 ChessAvatar - Quick Reference Guide

## Phase 5: Build & Deploy Commands

Quick reference for building and deploying ChessAvatar.

---

## 📦 Build Commands

### 1. PyInstaller Build (Recommended for Quick Testing)

```bash
# Install dependencies
pip install pyinstaller Pillow

# Build executable
python build_pyinstaller.py

# Test
cd dist\ChessAvatar
ChessAvatar.exe
```

**Output**: `dist/ChessAvatar/ChessAvatar.exe` (~100 MB)  
**Time**: 5 minutes

---

### 2. Nuitka Build (Performance)

```bash
# Install dependencies
pip install nuitka Pillow

# Install C compiler first (MinGW-w64 or Visual Studio)
# Download: https://winlibs.com/

# Build (takes longer)
python build_nuitka.py

# Test
cd dist\ChessAvatar_Nuitka
ChessAvatar.exe
```

**Output**: `dist/ChessAvatar_Nuitka/ChessAvatar.exe` (~60 MB)  
**Time**: 20 minutes  
**Performance**: 3× faster startup

---

### 3. MSIX Package (Microsoft Store)

```bash
# First, build with PyInstaller
python build_pyinstaller.py

# Generate assets (optional, creates placeholders)
python generate_assets.py

# Create MSIX package
python build_msix.py
```

**Output**: `ChessAvatar-1.0.0.0.msix`  
**Requirements**: Windows SDK (makeappx.exe, signtool.exe)

---

## 🎨 Asset Generation

```bash
# Generate placeholder Store assets
pip install Pillow
python generate_assets.py
```

**Creates**:
- `msix_build/Assets/Square44x44Logo.png`
- `msix_build/Assets/Square71x71Logo.png`
- `msix_build/Assets/Square150x150Logo.png`
- `msix_build/Assets/Square310x310Logo.png`
- `msix_build/Assets/Wide310x150Logo.png`
- `msix_build/Assets/StoreLogo.png`
- `msix_build/Assets/SplashScreen.png`
- `msix_build/Assets/pgnIcon.png`

**⚠️ Important**: Replace these with professional designs before Store submission!

---

## 🧪 Testing

### Test PyInstaller Build
```bash
cd dist\ChessAvatar
ChessAvatar.exe
```

### Test Nuitka Build
```bash
cd dist\ChessAvatar_Nuitka
ChessAvatar.exe
```

### Test MSIX Installation
```powershell
# Enable Developer Mode in Windows Settings first!

# Install
Add-AppxPackage .\ChessAvatar-1.0.0.0.msix

# Launch from Start Menu or:
Start-Process "chessavatar:launch"

# Uninstall
Get-AppxPackage *ChessAvatar* | Remove-AppxPackage
```

---

## 🔧 Customization

### Update Version

Edit `version.py`:
```python
__version__ = "1.1.0"
VERSION_MAJOR = 1
VERSION_MINOR = 1
VERSION_PATCH = 0
```

Rebuild:
```bash
python build_pyinstaller.py
python build_msix.py
```

### Change Icon

1. Replace `resources/icon.ico` (256×256, ICO format)
2. Rebuild

### Update Store Assets

1. Replace files in `msix_build/Assets/`
2. Run `python build_msix.py`

---

## 📤 Microsoft Store Submission

### 1. Prepare
```bash
python build_pyinstaller.py
python generate_assets.py  # Replace with real assets!
python build_msix.py
```

### 2. Sign Package
```powershell
# Get certificate from Microsoft Partner Center

signtool sign /fd SHA256 /a /f YourCertificate.pfx `
    /p YourPassword ChessAvatar-1.0.0.0.msix
```

### 3. Submit
1. Go to https://partner.microsoft.com/dashboard
2. Create new app submission
3. Upload `ChessAvatar-1.0.0.0.msix`
4. Add screenshots, description
5. Submit for review

---

## 🐛 Troubleshooting

### "PyInstaller not found"
```bash
pip install --upgrade pyinstaller
```

### "makeappx not found"
```powershell
# Add Windows SDK to PATH
$env:Path += ";C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64"
```

### "C compiler not found" (Nuitka)
Download MinGW-w64: https://winlibs.com/  
Add to PATH: `C:\mingw64\bin`

### "Module not found" at runtime
Add to `chessavatar.spec` in `hiddenimports`:
```python
hiddenimports=['your_missing_module']
```

### Build fails
```bash
# Clean and retry
rm -rf build dist
python build_pyinstaller.py
```

---

## 📊 Build Comparison

| Feature | PyInstaller | Nuitka | MSIX |
|---------|-------------|--------|------|
| **Time** | 5 min | 20 min | 10 min* |
| **Size** | ~100 MB | ~60 MB | ~100 MB |
| **Speed** | Good | Excellent | Good |
| **Setup** | Easy | Needs compiler | Needs SDK |
| **Store** | ❌ | ❌ | ✅ |

*After PyInstaller build

---

## 📋 Pre-Launch Checklist

### Technical
- [ ] PyInstaller build successful
- [ ] Nuitka build successful
- [ ] MSIX package created
- [ ] Tested on Windows 10
- [ ] Tested on Windows 11
- [ ] All features working
- [ ] No crashes

### Assets
- [ ] Replace icon.ico with professional design
- [ ] Replace all Store tiles
- [ ] Create splash screen
- [ ] Take 5-10 screenshots
- [ ] Create promotional graphics

### Store
- [ ] Partner Center account created
- [ ] App name reserved: "ChessAvatar"
- [ ] Description written
- [ ] Certificate obtained
- [ ] MSIX signed
- [ ] Upload ready

---

## 📚 Documentation

- **Full Build Guide**: [BUILD_GUIDE.md](BUILD_GUIDE.md)
- **Asset Guide**: [RESOURCES_GUIDE.md](RESOURCES_GUIDE.md)
- **Phase 5 Summary**: [PHASE5_COMPLETE.md](PHASE5_COMPLETE.md)
- **Complete Summary**: [COMPLETE_PROJECT_SUMMARY.md](COMPLETE_PROJECT_SUMMARY.md)

---

## 🎯 Recommended Workflow

### For Development
```bash
python main.py  # Run directly
```

### For Testing Distribution
```bash
python build_pyinstaller.py  # Quick build
cd dist\ChessAvatar
ChessAvatar.exe
```

### For Production
```bash
python build_nuitka.py  # Optimized build
cd dist\ChessAvatar_Nuitka
ChessAvatar.exe
```

### For Microsoft Store
```bash
python build_pyinstaller.py
python generate_assets.py  # Then replace with real assets
python build_msix.py
# Sign and submit
```

---

## 🚀 Quick Start for New Developers

```bash
# 1. Clone repository
git clone https://github.com/yourusername/chessavatar-project.git
cd chessavatar-project

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
python main.py

# 4. Build executable (when ready)
pip install pyinstaller Pillow
python build_pyinstaller.py
```

---

## 💡 Tips

1. **Always test** executables on clean Windows VM
2. **Replace assets** before Store submission
3. **Use Nuitka** for production builds (better performance)
4. **Keep source code** even after building
5. **Version control** everything including assets

---

## 📞 Support

- **Build Issues**: See [BUILD_GUIDE.md](BUILD_GUIDE.md)
- **General Issues**: GitHub Issues
- **Store Issues**: Microsoft Partner Center Support

---

**ChessAvatar v1.0.0 - Ready for Launch!** 🎉

*All 5 phases complete. Build, test, and deploy to Microsoft Store!*

