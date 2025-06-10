# ========== WORKSPACE AUTO-ACTIVATION PROFILE ==========
# Auto-activates BSPclean virtual environment for CursorMCPWorkspace
# Location: C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace
# Last updated: 2025-01-28

Write-Host "[WORKSPACE] 🔧 Initializing CursorMCPWorkspace profile..." -ForegroundColor Cyan

# Check if we're already in a virtual environment
if ($env:VIRTUAL_ENV) {
    Write-Host "[VENV] ✅ Already in virtual environment: $($env:VIRTUAL_ENV)" -ForegroundColor Green
} else {
    # Check if BSPclean virtual environment exists
    $venvPath = ".\BSPclean\Scripts\Activate.ps1"
    
    if (Test-Path $venvPath) {
        Write-Host "[VENV] 🔄 Activating BSPclean virtual environment..." -ForegroundColor Yellow
        
        # Activate the virtual environment
        & $venvPath
        
        # Verify activation
        if ($env:VIRTUAL_ENV) {
            Write-Host "[VENV] ✅ BSPclean virtual environment activated successfully" -ForegroundColor Green
            Write-Host "[VENV] 📍 Python location: $(Get-Command python).Source" -ForegroundColor Green
            Write-Host "[VENV] 🐍 Python version: $(python --version)" -ForegroundColor Green
            Write-Host "[VENV] 💾 MCP operations available: 29 registered operations" -ForegroundColor Green
        } else {
            Write-Host "[VENV] ❌ Failed to activate BSPclean virtual environment" -ForegroundColor Red
        }
    } else {
        Write-Host "[VENV] ⚠️  BSPclean virtual environment not found at: $venvPath" -ForegroundColor Yellow
        Write-Host "[VENV] 💡 Run setup_auto_venv.ps1 to create the virtual environment" -ForegroundColor Yellow
    }
}

Write-Host "[WORKSPACE] ✅ Workspace profile initialization complete" -ForegroundColor Green
Write-Host ""
