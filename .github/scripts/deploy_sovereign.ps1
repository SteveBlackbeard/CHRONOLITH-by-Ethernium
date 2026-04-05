# Ethernium Continuity Legacy - Sovereign Deployment Pipeline
# ============================================================
# This script validates, builds, and optionally publishes all three editions.
# Usage:
#   .\deploy_sovereign.ps1              # Build only (dry run)
#   .\deploy_sovereign.ps1 -Publish     # Build + Upload to PyPI

param (
    [switch]$Publish
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " CONTINUITY LEGACY: SOVEREIGN DEPLOYMENT PIPELINE v2.1.0 " -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

# --- Phase 1: Validation ---
Write-Host "[1/4] DNA Integrity Validation..." -ForegroundColor Yellow

Write-Host "  [*] Running Lite tests..." -ForegroundColor White
pytest continuity-lite/tests/test_lite_logic.py --tb=short -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [!] LITE TESTS FAILED. Aborting deployment." -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] Lite: 6/6 green" -ForegroundColor Green

Write-Host "  [*] Running Pro tests..." -ForegroundColor White
pytest continuity-pro/tests/test_parity_logic.py --tb=short -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [!] PRO TESTS FAILED. Aborting deployment." -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] Pro: green" -ForegroundColor Green

# --- Phase 2: Merkle Root Verification ---
Write-Host ""
Write-Host "[2/4] Merkle Root Crystallization..." -ForegroundColor Yellow
python continuity-lite/continuity_lite/continuity_legacy/run_continuity_lite.py check --repo-root .
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [!] DNA DRIFT DETECTED. Aborting deployment." -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] DNA Parity Confirmed" -ForegroundColor Green

# --- Phase 3: Build ---
Write-Host ""
Write-Host "[3/4] Building Sovereign Packages..." -ForegroundColor Yellow
python -m pip install --upgrade build twine -q

$editions = @("continuity-lite", "continuity-pro", "continuity-omega")
foreach ($edition in $editions) {
    Write-Host "  [*] Building $edition..." -ForegroundColor White
    Push-Location $edition
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    python -m build --no-isolation 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [!] BUILD FAILED for $edition" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Write-Host "  [OK] $edition built successfully" -ForegroundColor Green
    Pop-Location
}

# --- Phase 4: Publish (optional) ---
if ($Publish) {
    Write-Host ""
    Write-Host "[4/4] Publishing to PyPI..." -ForegroundColor Yellow
    Write-Host "  [!] This will make packages PUBLIC. Confirm? (Ctrl+C to abort)" -ForegroundColor Red
    Start-Sleep -Seconds 3
    
    foreach ($edition in $editions) {
        Write-Host "  [*] Uploading $edition..." -ForegroundColor White
        python -m twine upload "$edition/dist/*"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  [!] UPLOAD FAILED for $edition" -ForegroundColor Red
            exit 1
        }
        Write-Host "  [OK] $edition published" -ForegroundColor Green
    }
} else {
    Write-Host ""
    Write-Host "[4/4] Skipping PyPI upload (dry run mode)" -ForegroundColor DarkGray
    Write-Host "  Run with -Publish flag to upload: .\deploy_sovereign.ps1 -Publish" -ForegroundColor DarkGray
}

# --- Summary ---
Write-Host ""
Write-Host "=========================================================" -ForegroundColor Green
Write-Host " SOVEREIGN DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  ethernium-continuity-lite   -> pip install ethernium-continuity-lite" -ForegroundColor Cyan
Write-Host "  ethernium-continuity-pro    -> pip install ethernium-continuity-pro" -ForegroundColor Magenta
Write-Host "  ethernium-continuity-omega  -> pip install ethernium-continuity-omega" -ForegroundColor Blue
Write-Host ""
