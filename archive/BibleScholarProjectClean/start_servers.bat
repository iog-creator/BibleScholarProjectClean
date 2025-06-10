@echo off
call scripts\clean_logs.bat
if not exist logs mkdir logs

echo [%DATE% %TIME%] Starting servers... >> logs\server_management.log

:: Check for port conflicts
netstat -ano | findstr :5000 >nul && (
    echo Port 5000 in use! Run stop_servers.bat first.
    echo [%DATE% %TIME%] ERROR: Port 5000 in use. >> logs\server_management.log
    exit /b 1
)
netstat -ano | findstr :5001 >nul && (
    echo Port 5001 in use! Run stop_servers.bat first.
    echo [%DATE% %TIME%] ERROR: Port 5001 in use. >> logs\server_management.log
    exit /b 1
)
netstat -ano | findstr :5002 >nul && (
    echo Port 5002 in use! Run stop_servers.bat first.
    echo [%DATE% %TIME%] ERROR: Port 5002 in use. >> logs\server_management.log
    exit /b 1
)

:: Start each server in its own window
start "API Server" cmd /c scripts\run_api_server.bat
start "Web UI Server" cmd /c scripts\run_web_app.bat
start "Contextual Insights" cmd /c scripts\run_contextual_insights.bat

timeout /t 10 >nul

:: Health checks
curl -s http://localhost:5000/health >nul && (
    echo API Server is running.
    echo [%DATE% %TIME%] API Server health check passed. >> logs\server_management.log
) || (
    echo API Server failed to start!
    echo [%DATE% %TIME%] ERROR: API Server health check failed. >> logs\server_management.log
)
curl -s http://localhost:5001/health >nul && (
    echo Web UI Server is running.
    echo [%DATE% %TIME%] Web UI Server health check passed. >> logs\server_management.log
) || (
    echo Web UI Server failed to start!
    echo [%DATE% %TIME%] ERROR: Web UI Server health check failed. >> logs\server_management.log
)
curl -s http://localhost:5002/health >nul && (
    echo Contextual Insights Server is running.
    echo [%DATE% %TIME%] Contextual Insights Server health check passed. >> logs\server_management.log
) || (
    echo Contextual Insights Server failed to start!
    echo [%DATE% %TIME%] ERROR: Contextual Insights Server health check failed. >> logs\server_management.log
)

echo [%DATE% %TIME%] Server startup complete. >> logs\server_management.log 