@echo off
chcp 65001>nul
REM Start Teaching server (Contextual Insights) independently
echo Starting Teaching server...
cd /d "%~dp0.."
call "%~dp0\run_contextual_insights.bat"
echo Teaching server start command issued. 