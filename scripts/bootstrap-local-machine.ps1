[CmdletBinding()]
param(
    [string]$RootPath = (Get-Location).Path,
    [string]$VenvName = ".venv",
    [ValidateSet("openclaw", "ollama", "moltbot")]
    [string]$ChatProvider = "openclaw",
    [string]$OpenClawBaseUrl = "http://127.0.0.1:3001",
    [string]$OllamaBaseUrl = "http://127.0.0.1:11434",
    [string]$MoltbotBaseUrl = "http://127.0.0.1:3002",
    [string]$OllamaModel = "llama3.1",
    [switch]$SkipDashboard,
    [switch]$StartDashboard,
    [string]$ConektaPath = "..\conekta-dev-by-ethernium"
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Assert-Path {
    param([string]$PathToCheck, [string]$Message)
    if (-not (Test-Path $PathToCheck)) {
        throw $Message
    }
}

function Set-Or-AppendEnvLine {
    param(
        [string]$FilePath,
        [string]$Key,
        [string]$Value
    )

    $escapedKey = [regex]::Escape($Key)
    $lines = if (Test-Path $FilePath) { Get-Content $FilePath -Encoding UTF8 } else { @() }

    $updated = $false
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match "^${escapedKey}=") {
            $lines[$i] = "$Key=$Value"
            $updated = $true
        }
    }

    if (-not $updated) {
        $lines += "$Key=$Value"
    }

    [System.IO.File]::WriteAllLines($FilePath, $lines, [System.Text.UTF8Encoding]::new($false))
}

$repoRoot = (Resolve-Path $RootPath).Path
$venvPath = Join-Path $repoRoot $VenvName
$conektaPath = if ([System.IO.Path]::IsPathRooted($ConektaPath)) { $ConektaPath } else { Join-Path $repoRoot $ConektaPath }
$conektaEnvExample = Join-Path $conektaPath ".env.example"
$conektaEnvLocal = Join-Path $conektaPath ".env.local"

$rootWheel = Get-ChildItem (Join-Path $repoRoot "dist") -Filter "ethernium_continuity_legacy-*.whl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$liteWheel = Get-ChildItem (Join-Path $repoRoot "continuity-lite\dist") -Filter "ethernium_continuity_lite-*.whl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$proWheel = Get-ChildItem (Join-Path $repoRoot "continuity-pro\dist") -Filter "ethernium_continuity_pro-*.whl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$omegaWheel = Get-ChildItem (Join-Path $repoRoot "continuity-omega\dist") -Filter "ethernium_continuity_omega-*.whl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

Assert-Path $repoRoot "Repository root not found: $repoRoot"
if (-not $rootWheel) { throw "Missing root wheel in dist/. Build artifacts are required before bootstrap." }
if (-not $liteWheel) { throw "Missing Lite wheel in continuity-lite/dist/." }
if (-not $proWheel) { throw "Missing Pro wheel in continuity-pro/dist/." }
if (-not $omegaWheel) { throw "Missing Omega wheel in continuity-omega/dist/." }

Write-Step "Creating or reusing virtual environment at $venvPath"
if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
}

$venvPython = Join-Path $venvPath "Scripts\python.exe"
$venvPip = Join-Path $venvPath "Scripts\pip.exe"

Assert-Path $venvPython "Virtual environment python not found at $venvPython"
Assert-Path $venvPip "Virtual environment pip not found at $venvPip"

Write-Step "Upgrading pip in the virtual environment"
& $venvPython -m pip install --upgrade pip

Write-Step "Installing local wheel artifacts"
& $venvPip install $rootWheel.FullName
& $venvPip install $liteWheel.FullName
& $venvPip install $proWheel.FullName
& $venvPip install $omegaWheel.FullName

Write-Step "Validating core Continuity CLI commands"
& $venvPython -m continuity_legacy --help | Out-Null
& $venvPython -m continuity_legacy status | Out-Null
& $venvPython -m continuity_legacy init --help | Out-Null

if (-not $SkipDashboard -and (Test-Path $conektaPath)) {
    Write-Step "Preparing Conekta Dev environment"
    Assert-Path $conektaEnvExample "Missing Conekta env template: $conektaEnvExample"
    if (-not (Test-Path $conektaEnvLocal)) {
        Copy-Item $conektaEnvExample $conektaEnvLocal
    }

    Set-Or-AppendEnvLine -FilePath $conektaEnvLocal -Key "CONTINUITY_CHAT_PROVIDER" -Value $ChatProvider
    Set-Or-AppendEnvLine -FilePath $conektaEnvLocal -Key "CONTINUITY_OPENCLAW_BASE_URL" -Value $OpenClawBaseUrl
    Set-Or-AppendEnvLine -FilePath $conektaEnvLocal -Key "CONTINUITY_OLLAMA_BASE_URL" -Value $OllamaBaseUrl
    Set-Or-AppendEnvLine -FilePath $conektaEnvLocal -Key "CONTINUITY_MOLTBOT_BASE_URL" -Value $MoltbotBaseUrl
    Set-Or-AppendEnvLine -FilePath $conektaEnvLocal -Key "CONTINUITY_OLLAMA_MODEL" -Value $OllamaModel
    Set-Or-AppendEnvLine -FilePath $conektaEnvLocal -Key "CONTINUITY_OPENCLAW_ENABLED" -Value ($(if ($ChatProvider -eq "openclaw") { "true" } else { "false" }))
    Set-Or-AppendEnvLine -FilePath $conektaEnvLocal -Key "CONTINUITY_OLLAMA_ENABLED" -Value ($(if ($ChatProvider -eq "ollama") { "true" } else { "false" }))
    Set-Or-AppendEnvLine -FilePath $conektaEnvLocal -Key "CONTINUITY_MOLTBOT_ENABLED" -Value ($(if ($ChatProvider -eq "moltbot") { "true" } else { "false" }))

    Write-Step "Installing Conekta Dev dependencies"
    Push-Location $conektaPath
    try {
        npm install

        Write-Step "Building Conekta Dev"
        npm run build

        if ($StartDashboard) {
            Write-Step "Starting Conekta Dev"
            npm run start
        }
    }
    finally {
        Pop-Location
    }
} elseif (-not $SkipDashboard) {
    Write-Step "Conekta Dev not found at $conektaPath; skipping external UI bootstrap"
}

Write-Step "Bootstrap complete"
Write-Host "Virtual environment: $venvPath" -ForegroundColor Green
Write-Host "Conekta Dev path: $conektaPath" -ForegroundColor Green
Write-Host "Chat provider: $ChatProvider" -ForegroundColor Green
Write-Host ""
Write-Host "PyPI upload was intentionally skipped." -ForegroundColor Yellow
Write-Host "When ready, upload from a machine with Twine credentials using:" -ForegroundColor Yellow
Write-Host "  python -m twine upload dist/ethernium_continuity_legacy-*.whl dist/ethernium_continuity_legacy-*.tar.gz"
Write-Host "  python -m twine upload continuity-lite/dist/ethernium_continuity_lite-*.whl continuity-lite/dist/ethernium_continuity_lite-*.tar.gz"
Write-Host "  python -m twine upload continuity-pro/dist/ethernium_continuity_pro-*.whl continuity-pro/dist/ethernium_continuity_pro-*.tar.gz"
Write-Host "  python -m twine upload continuity-omega/dist/ethernium_continuity_omega-*.whl continuity-omega/dist/ethernium_continuity_omega-*.tar.gz"
