# BibleScholarLangChain Environment Activation Script
# This script activates the BSPclean virtual environment and navigates to the project directory

Write-Host "Activating BSPclean virtual environment..." -ForegroundColor Green

# Activate the virtual environment
& "C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BSPclean\Scripts\Activate.ps1"

# Navigate to the project directory
Set-Location "C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BibleScholarLangChain"

Write-Host "Environment activated successfully!" -ForegroundColor Green
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
Write-Host "Python version: $(python --version)" -ForegroundColor Yellow
Write-Host "Virtual environment: $env:VIRTUAL_ENV" -ForegroundColor Yellow

Write-Host "`nReady to work on BibleScholarLangChain project!" -ForegroundColor Cyan 