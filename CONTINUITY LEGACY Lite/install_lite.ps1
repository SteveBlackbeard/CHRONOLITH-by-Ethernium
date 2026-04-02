param(
    [Parameter(Mandatory=$false)]
    [string]$Target = ".\MyProject"
)

Write-Host "[*] CONTINUITY LEGACY Lite - Installer"
$targetDir = Resolve-Path -Path $Target -ErrorAction SilentlyContinue

if (-not $targetDir) {
    New-Item -ItemType Directory -Force -Path $Target | Out-Null
    $targetDir = Resolve-Path -Path $Target
}

Write-Host "[->] Installing zero-overhead continuity into '$targetDir'..."

# Create boilerplate markdown and json
$projectContext = @"
# PROJECT CONTEXT
Describe the overall project goal and stack here.

## Rules
1. Document every decision.
"@

$liveHandoff = @"
# LIVE HANDOFF
Here is where the last agent left off.

## Next Exact Action
Write the next immediate step for the agent here.
"@

$stateJson = @"
{
  "status": "active",
  "project_name": "New Lite Project",
  "last_sync": "",
  "git_branch": "",
  "git_commit": ""
}
"@

# The run script
$runScriptSrc = Join-Path -Path $PSScriptRoot -ChildPath "run_continuity_lite.py"
$runScriptDest = Join-Path -Path $targetDir -ChildPath "run_continuity_lite.py"

if (Test-Path $runScriptSrc) {
    Copy-Item -Path $runScriptSrc -Destination $runScriptDest -Force
} else {
    Write-Host "[!] Could not find 'run_continuity_lite.py' to copy. Ensure it exists next to this installer." -ForegroundColor Red
    exit 1
}

Set-Content -Path (Join-Path -Path $targetDir -ChildPath "PROJECT_CONTEXT.md") -Value $projectContext
Set-Content -Path (Join-Path -Path $targetDir -ChildPath "LIVE_HANDOFF.md") -Value $liveHandoff
Set-Content -Path (Join-Path -Path $targetDir -ChildPath "STATE.json") -Value $stateJson

Write-Host "[✔] CONTINUITY LEGACY Lite installed successfully!" -ForegroundColor Green
Write-Host "    To use it, run 'python run_continuity_lite.py' inside your project root."
