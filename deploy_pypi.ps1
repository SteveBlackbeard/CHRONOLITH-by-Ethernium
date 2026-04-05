# Ethernium Continuity Legacy - PyPI Publishing Script

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " CONTINUITY LEGACY: GLOBAL PYPI DEPLOYMENT INITIATED " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Install dependencies if missing
python -m pip install --upgrade pip build twine

# Helper to build and deploy
function Deploy-Edition {
    param ( [string]$EditionName )
    Write-Host "`n[*] Empaquetando y Desplegando: $EditionName ..." -ForegroundColor Yellow
    Set-Location $EditionName
    
    # Clean previous builds
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    
    # Build Wheel & Tar
    python -m build
    
    # Upload to PyPI
    python -m twine upload dist/*
    
    Set-Location ..
}

# Deploy process
Deploy-Edition "continuity-lite"
Deploy-Edition "continuity-pro"
Deploy-Edition "continuity-omega"

Write-Host "`n[OK] DEPLOYMENT COMPLETO." -ForegroundColor Green
Write-Host "Instalacion global lista vía: pip install continuity-omega" -ForegroundColor Green
