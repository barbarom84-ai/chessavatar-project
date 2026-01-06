# Script PowerShell pour signer le package MSIX
# Utilisation : .\sign_package.ps1 -CertPassword "VotreMotDePasse"

param(
    [Parameter(Mandatory=$false)]
    [string]$PackagePath = "ChessAvatar-1.0.0.0.msix",
    
    [Parameter(Mandatory=$false)]
    [string]$CertPath = "ChessAvatar_Certificate.pfx",
    
    [Parameter(Mandatory=$true)]
    [string]$CertPassword
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ChessAvatar - Package Signing Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Vérifier que le package existe
if (-not (Test-Path $PackagePath)) {
    Write-Host "❌ Package not found: $PackagePath" -ForegroundColor Red
    Write-Host "   Run: python build_msix.py first" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found package: $PackagePath" -ForegroundColor Green

# Vérifier que le certificat existe
if (-not (Test-Path $CertPath)) {
    Write-Host "❌ Certificate not found: $CertPath" -ForegroundColor Red
    Write-Host "" -ForegroundColor Yellow
    Write-Host "To create a test certificate:" -ForegroundColor Yellow
    Write-Host "  New-SelfSignedCertificate -Type Custom ``" -ForegroundColor Cyan
    Write-Host "      -Subject 'CN=ChessAvatarTeam' ``" -ForegroundColor Cyan
    Write-Host "      -KeyUsage DigitalSignature ``" -ForegroundColor Cyan
    Write-Host "      -FriendlyName 'ChessAvatar Test Certificate' ``" -ForegroundColor Cyan
    Write-Host "      -CertStoreLocation 'Cert:\CurrentUser\My'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Then export it:" -ForegroundColor Yellow
    Write-Host "  `$pwd = ConvertTo-SecureString -String 'YourPassword' -Force -AsPlainText" -ForegroundColor Cyan
    Write-Host "  `$cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object {`$_.Subject -like '*ChessAvatarTeam*'}" -ForegroundColor Cyan
    Write-Host "  Export-PfxCertificate -Cert `$cert -FilePath 'ChessAvatar_Certificate.pfx' -Password `$pwd" -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ Found certificate: $CertPath" -ForegroundColor Green

# Vérifier que signtool est disponible
$signtool = Get-Command signtool -ErrorAction SilentlyContinue
if (-not $signtool) {
    Write-Host "❌ signtool.exe not found" -ForegroundColor Red
    Write-Host "   Install Windows SDK: https://developer.microsoft.com/windows/downloads/windows-sdk/" -ForegroundColor Yellow
    Write-Host "   Or add to PATH:" -ForegroundColor Yellow
    Write-Host "   C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64" -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ Found signtool.exe" -ForegroundColor Green
Write-Host ""

# Signer le package
Write-Host "🔐 Signing package..." -ForegroundColor Yellow

try {
    & signtool sign /fd SHA256 /a /f $CertPath /p $CertPassword $PackagePath 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Package signed successfully!" -ForegroundColor Green
        
        # Vérifier la signature
        Write-Host ""
        Write-Host "🔍 Verifying signature..." -ForegroundColor Yellow
        
        & signtool verify /pa $PackagePath 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Signature verified!" -ForegroundColor Green
            
            # Afficher les informations de signature
            Write-Host ""
            Write-Host "📜 Signature details:" -ForegroundColor Cyan
            & signtool verify /pa /v $PackagePath | Select-String "Signing Certificate Chain", "Issued to", "Issued by", "Expires"
            
        } else {
            Write-Host "⚠️  Signature verification failed" -ForegroundColor Yellow
            Write-Host "   Package is signed but may not be trusted on this machine" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  ✅ Signing Complete!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "1. Test installation: Add-AppxPackage $PackagePath" -ForegroundColor White
        Write-Host "2. Upload to Microsoft Partner Center" -ForegroundColor White
        Write-Host "3. Submit for review" -ForegroundColor White
        
    } else {
        Write-Host "❌ Signing failed!" -ForegroundColor Red
        Write-Host "   Check certificate password and validity" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Error during signing: $_" -ForegroundColor Red
    exit 1
}

