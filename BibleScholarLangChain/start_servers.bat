@echo off
REM Start BibleScholarLangChain servers
REM Kills existing processes and starts servers sequentially with proper environment

echo ========================================
echo Starting BibleScholarLangChain servers
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

REM Kill existing processes on ports 5000 and 5002
echo Killing existing processes on ports 5000 and 5002...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do (
    echo Killing process %%a on port 5000
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5002" ^| find "LISTENING"') do (
    echo Killing process %%a on port 5002
    taskkill /f /pid %%a >nul 2>&1
)

REM Wait for ports to be free
echo Waiting for ports to be free...
timeout /t 3 /nobreak >nul

REM Start API server on port 5000 in background with virtual environment
echo Starting API server on port 5000...
start "BibleScholar API Server" /min cmd /c "call "%ACTIVATE_SCRIPT%" && cd /d "%PROJECT_DIR%" && python src\api\api_app.py"

REM Wait and test API server
echo Waiting for API server to start...
timeout /t 8 /nobreak >nul

REM Test API server health
echo Testing API server health...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5000/health' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Host 'API Server: HEALTHY' -ForegroundColor Green } else { Write-Host 'API Server: UNHEALTHY' -ForegroundColor Red } } catch { Write-Host 'API Server: NOT RESPONDING' -ForegroundColor Red }"

REM Start Web UI server on port 5002 in background with virtual environment
echo Starting Web UI server on port 5002...
start "BibleScholar Web UI" /min cmd /c "call "%ACTIVATE_SCRIPT%" && cd /d "%PROJECT_DIR%" && python web_app.py"

REM Wait and test Web UI server
echo Waiting for Web UI server to start...
timeout /t 8 /nobreak >nul

REM Test Web UI server health
echo Testing Web UI server health...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5002/health' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Host 'Web UI Server: HEALTHY' -ForegroundColor Green } else { Write-Host 'Web UI Server: UNHEALTHY' -ForegroundColor Red } } catch { Write-Host 'Web UI Server: NOT RESPONDING' -ForegroundColor Red }"

REM Final status check
echo.
echo ========================================
echo Server Status Summary
echo ========================================
netstat -an | find ":5000" | find "LISTENING" >nul && echo Port 5000 (API): LISTENING || echo Port 5000 (API): NOT LISTENING
netstat -an | find ":5002" | find "LISTENING" >nul && echo Port 5002 (Web UI): LISTENING || echo Port 5002 (Web UI): NOT LISTENING

echo.
echo ========================================
echo Access URLs
echo ========================================
echo API Server: http://localhost:5000
echo Web UI: http://localhost:5002
echo Search Interface: http://localhost:5002/search
echo Study Dashboard: http://localhost:5002/study_dashboard
echo Tutor Interface: http://localhost:5002/tutor
echo.
echo ========================================
echo Logs Location
echo ========================================
echo Web UI Logs: %PROJECT_DIR%\logs\web_app.log
echo.
echo Servers are running in background windows.
echo Close this window or press Ctrl+C to exit (servers will continue running).
echo To stop servers, run this script again or kill the processes manually.
echo.
pause 