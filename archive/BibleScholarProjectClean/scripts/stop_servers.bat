@echo off
if not exist logs mkdir logs

echo Stopping all server processes...
echo [%DATE% %TIME%] Stopping servers... >> "logs\server_management.log"

taskkill /F /IM python.exe /T >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python processes terminated successfully.
    echo [%DATE% %TIME%] Python processes terminated. >> "logs\server_management.log"
) else (
    echo Failed to terminate some Python processes.
    echo [%DATE% %TIME%] ERROR: Failed to terminate Python processes. >> "logs\server_management.log"
)

timeout /t 5 >nul

netstat -ano | findstr :5000 >nul && (
    echo Port 5000 still in use!
    echo [%DATE% %TIME%] WARNING: Port 5000 still in use. >> "logs\server_management.log"
) || (
    echo Port 5000 is free.
    echo [%DATE% %TIME%] Port 5000 freed. >> "logs\server_management.log"
)
netstat -ano | findstr :5001 >nul && (
    echo Port 5001 still in use!
    echo [%DATE% %TIME%] WARNING: Port 5001 still in use. >> "logs\server_management.log"
) || (
    echo Port 5001 is free.
    echo [%DATE% %TIME%] Port 5001 freed. >> "logs\server_management.log"
)
netstat -ano | findstr :5002 >nul && (
    echo Port 5002 still in use!
    echo [%DATE% %TIME%] WARNING: Port 5002 still in use. >> "logs\server_management.log"
) || (
    echo Port 5002 is free.
    echo [%DATE% %TIME%] Port 5002 freed. >> "logs\server_management.log"
)

echo All servers stopped.
echo [%DATE% %TIME%] Server shutdown complete. >> "logs\server_management.log" 