@echo off
REM Start BibleScholarLangChain servers
REM Kills existing processes and starts servers sequentially with proper environment
REM UPDATED: Using standardized ports 5200 (API) and 5300 (Web UI)

echo ========================================
echo Starting BibleScholarLangChain servers
echo STANDARDIZED PORTS: API=5200, Web UI=5300
echo ========================================

REM Set environment variables
set PYTHONPATH=C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace
set VENV_DIR=C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BSPclean
set PYTHON_EXE=%VENV_DIR%\Scripts\python.exe
set ACTIVATE_SCRIPT=%VENV_DIR%\Scripts\activate.bat
set PROJECT_DIR=C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BibleScholarLangChain

REM Verify virtual environment exists
if not exist "%VENV_DIR%" (
    echo ERROR: Virtual environment not found at %VENV_DIR%
    echo Please ensure BSPclean virtual environment is set up correctly
    pause
    exit /b 1
)

REM Verify Python executable exists
if not exist "%PYTHON_EXE%" (
    echo ERROR: Python executable not found at %PYTHON_EXE%
    echo Please ensure BSPclean virtual environment is set up correctly
    pause
    exit /b 1
)

REM Verify activation script exists
if not exist "%ACTIVATE_SCRIPT%" (
    echo ERROR: Activation script not found at %ACTIVATE_SCRIPT%
    echo Please ensure BSPclean virtual environment is set up correctly
    pause
    exit /b 1
)

REM Verify project directory exists
if not exist "%PROJECT_DIR%" (
    echo ERROR: Project directory not found at %PROJECT_DIR%
    pause
    exit /b 1
)

REM Change to project directory first
cd /d "%PROJECT_DIR%"

REM Verify required files exist
if not exist "src\api\api_app.py" (
    echo ERROR: API server file not found at src\api\api_app.py
    pause
    exit /b 1
)

if not exist "web_app.py" (
    echo ERROR: Web app file not found at web_app.py
    pause
    exit /b 1
)

REM Kill existing processes on ports 5200 and 5300 (new standardized ports)
echo Killing existing processes on ports 5200 and 5300...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5200" ^| find "LISTENING"') do (
    echo Killing process %%a on port 5200
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5300" ^| find "LISTENING"') do (
    echo Killing process %%a on port 5300
    taskkill /f /pid %%a >nul 2>&1
)

REM Also kill old ports 5000 and 5002 for cleanup
echo Cleaning up old ports 5000 and 5002...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do (
    echo Killing process %%a on old port 5000
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5002" ^| find "LISTENING"') do (
    echo Killing process %%a on old port 5002
    taskkill /f /pid %%a >nul 2>&1
)

REM Wait for ports to be free
echo Waiting for ports to be free...
timeout /t 3 /nobreak >nul

REM Start API server on port 5200 in background with virtual environment
echo Starting Enhanced API server on port 5200...
start "BibleScholar Enhanced API Server" /min cmd /c "call "%ACTIVATE_SCRIPT%" && cd /d "%PROJECT_DIR%" && python src\api\api_app.py"

REM Wait and test API server
echo Waiting for API server to start...
timeout /t 8 /nobreak >nul

REM Test API server health
echo Testing API server health...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5200/health' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Host 'Enhanced API Server: HEALTHY' -ForegroundColor Green } else { Write-Host 'Enhanced API Server: UNHEALTHY' -ForegroundColor Red } } catch { Write-Host 'Enhanced API Server: NOT RESPONDING' -ForegroundColor Red }"

REM Start Web UI server on port 5300 in background with virtual environment
echo Starting Enhanced Web UI server on port 5300...
start "BibleScholar Enhanced Web UI" /min cmd /c "call "%ACTIVATE_SCRIPT%" && cd /d "%PROJECT_DIR%" && python web_app.py"

REM Wait and test Web UI server
echo Waiting for Web UI server to start...
timeout /t 8 /nobreak >nul

REM Test Web UI server health
echo Testing Web UI server health...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5300/health' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Host 'Enhanced Web UI Server: HEALTHY' -ForegroundColor Green } else { Write-Host 'Enhanced Web UI Server: UNHEALTHY' -ForegroundColor Red } } catch { Write-Host 'Enhanced Web UI Server: NOT RESPONDING' -ForegroundColor Red }"

REM Final status check
echo.
echo ========================================
echo Server Status Summary (STANDARDIZED PORTS)
echo ========================================
netstat -an | find ":5200" | find "LISTENING" >nul && echo Port 5200 (Enhanced API): LISTENING || echo Port 5200 (Enhanced API): NOT LISTENING
netstat -an | find ":5300" | find "LISTENING" >nul && echo Port 5300 (Enhanced Web UI): LISTENING || echo Port 5300 (Enhanced Web UI): NOT LISTENING

echo.
echo ========================================
echo Access URLs (STANDARDIZED PORTS)
echo ========================================
echo Enhanced API Server: http://localhost:5200
echo Enhanced API Health: http://localhost:5200/health
echo Enhanced API Contextual Insights: http://localhost:5200/api/contextual_insights/insights
echo.
echo Enhanced Web UI: http://localhost:5300
echo Enhanced Web UI Health: http://localhost:5300/health
echo Search Interface: http://localhost:5300/search
echo Study Dashboard: http://localhost:5300/study_dashboard
echo Tutor Interface: http://localhost:5300/tutor
echo Contextual Insights UI: http://localhost:5300/contextual-insights
echo.
echo ========================================
echo Enhanced Features Available
echo ========================================
echo - Comprehensive John 1:1 analysis with cross-references
echo - Multi-translation support: KJV, ASV, YLT, TAHOT
echo - Greek/Hebrew morphological analysis
echo - Semantic verse matching
echo - Enhanced biblical insights with LM Studio integration
echo.
echo ========================================
echo Logs Location
echo ========================================
echo Web UI Logs: %PROJECT_DIR%\logs\web_app.log
echo API Logs: %PROJECT_DIR%\logs\api.log
echo MCP Operations: C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\logs\mcp_operations\
echo.
echo Servers are running in background windows.
echo Close this window or press Ctrl+C to exit (servers will continue running).
echo To stop servers, run this script again or kill the processes manually.
echo.
pause 