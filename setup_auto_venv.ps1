#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Configure PowerShell to automatically start in BSPclean virtual environment
.DESCRIPTION
    This script sets up automatic BSPclean venv activation for Cursor PowerShell sessions
    and fixes the yellow warning state in the PowerShell extension.
#>

Write-Host "=== SETTING UP AUTO-VENV ACTIVATION ===" -ForegroundColor Green

# Check if we're in the workspace root
$WorkspaceRoot = "C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace"
$CurrentPath = Get-Location

if ($CurrentPath.Path -ne $WorkspaceRoot) {
    Write-Host "❌ Must run from workspace root: $WorkspaceRoot" -ForegroundColor Red
    Write-Host "Current location: $($CurrentPath.Path)" -ForegroundColor Yellow
    exit 1
}

# Check if BSPclean venv exists
$VenvPath = Join-Path $WorkspaceRoot "BSPclean"
$VenvActivate = Join-Path $VenvPath "Scripts\Activate.ps1"

if (-not (Test-Path $VenvActivate)) {
    Write-Host "❌ BSPclean virtual environment not found at: $VenvPath" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found BSPclean venv at: $VenvPath" -ForegroundColor Green

# Create workspace-specific PowerShell profile
$ProfileContent = @"
# Auto-activate BSPclean virtual environment for CursorMCPWorkspace
if (`$PWD.Path -eq "$WorkspaceRoot") {
    if (-not `$env:VIRTUAL_ENV) {
        Write-Host "🔧 Auto-activating BSPclean virtual environment..." -ForegroundColor Yellow
        & "$VenvActivate"
        Write-Host "✅ BSPclean virtual environment activated" -ForegroundColor Green
        Write-Host "Python: `$(python --version)" -ForegroundColor Cyan
        Write-Host "Location: `$(python -c 'import sys; print(sys.executable)')" -ForegroundColor Cyan
    }
}
"@

# Save profile to workspace
$WorkspaceProfile = Join-Path $WorkspaceRoot "workspace_profile.ps1"
Set-Content -Path $WorkspaceProfile -Value $ProfileContent -Encoding UTF8

Write-Host "✅ Created workspace PowerShell profile: $WorkspaceProfile" -ForegroundColor Green

# Create Cursor workspace settings to use the profile
$CursorDir = Join-Path $WorkspaceRoot ".vscode"
if (-not (Test-Path $CursorDir)) {
    New-Item -Path $CursorDir -ItemType Directory -Force | Out-Null
}

$SettingsFile = Join-Path $CursorDir "settings.json"
$CursorSettings = @{
    "terminal.integrated.defaultProfile.windows" = "PowerShell"
    "terminal.integrated.profiles.windows" = @{
        "PowerShell" = @{
            "source" = "PowerShell"
            "args" = @(
                "-NoExit",
                "-Command",
                "& '$WorkspaceProfile'"
            )
        }
    }
    "terminal.integrated.cwd" = $WorkspaceRoot
    "python.defaultInterpreterPath" = "$VenvPath\Scripts\python.exe"
    "python.terminal.activateEnvironment" = $false  # We handle activation manually
}

# Convert to JSON and save
$SettingsJson = $CursorSettings | ConvertTo-Json -Depth 10
Set-Content -Path $SettingsFile -Value $SettingsJson -Encoding UTF8

Write-Host "✅ Updated Cursor workspace settings: $SettingsFile" -ForegroundColor Green

# Test the setup
Write-Host "" 
Write-Host "=== TESTING SETUP ===" -ForegroundColor Yellow
Write-Host "Testing BSPclean activation..."

try {
    & $VenvActivate
    $PythonVersion = python --version
    $PythonPath = python -c "import sys; print(sys.executable)"
    
    Write-Host "✅ Test successful!" -ForegroundColor Green
    Write-Host "  Python Version: $PythonVersion" -ForegroundColor Cyan
    Write-Host "  Python Path: $PythonPath" -ForegroundColor Cyan
    
    # Test MCP operations
    $MCPTest = python -c "from mcp_universal_operations import universal_router; print(f'MCP Operations: {len(universal_router.operation_registry)}')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  $MCPTest" -ForegroundColor Cyan
    }
    
} catch {
    Write-Host "❌ Test failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== NEXT STEPS ===" -ForegroundColor Yellow
Write-Host "1. Kill the PowerShell extension in Cursor (Ctrl+Shift+P > 'PowerShell: Restart Session')"
Write-Host "2. Open a new terminal - it should automatically activate BSPclean venv"
Write-Host "3. Verify you see '(BSPclean) PS>' in the prompt"
Write-Host "4. The yellow warning should be gone after restart"
Write-Host ""
Write-Host "✅ Auto-venv setup complete!" -ForegroundColor Green 