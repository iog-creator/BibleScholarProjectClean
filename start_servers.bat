@echo off
echo Starting BibleScholarLangChain servers...

REM Set paths
set PROJECT_ROOT=C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace
set VENV_PATH=%PROJECT_ROOT%/BSPclean
set BIBLESCHOLAR_DIR=%PROJECT_ROOT%/BibleScholarLangChain

REM Check if virtual environment exists
if not exist "%VENV_PATH%/Scripts/python.exe" (
    echo ERROR: Virtual environment not found at %VENV_PATH%
    echo Please ensure BSPclean virtual environment is set up correctly
    pause
    exit /b 1
)

REM Check if BibleScholarLangChain directory exists
if not exist "%BIBLESCHOLAR_DIR%" (
    echo ERROR: BibleScholarLangChain directory not found at %BIBLESCHOLAR_DIR%
    pause
    exit /b 1
)

REM Kill any existing processes on ports 5000 and 5002
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

REM Start API server (run from BibleScholarLangChain directory)
echo Starting API server on port 5000...
start "BibleScholar API Server" /min cmd /c "cd /d "%BIBLESCHOLAR_DIR%" && "%VENV_PATH%/Scripts/python.exe" src/api/api_app.py"

REM Wait for API server to start
echo Waiting for API server to start...
timeout /t 8 /nobreak >nul

REM Test API server health
echo Testing API server health...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5000/health' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Host 'API Server: HEALTHY' -ForegroundColor Green } else { Write-Host 'API Server: UNHEALTHY' -ForegroundColor Red } } catch { Write-Host 'API Server: NOT RESPONDING' -ForegroundColor Red }"

REM Start Web UI server (run from BibleScholarLangChain directory)
echo Starting Web UI server on port 5002...
start "BibleScholar Web UI" /min cmd /c "cd /d "%BIBLESCHOLAR_DIR%" && "%VENV_PATH%/Scripts/python.exe" web_app.py"

REM Wait for Web UI server to start
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
echo.
echo Servers are running in background windows.
echo Close this window or press Ctrl+C to exit (servers will continue running).
echo To stop servers, run this script again or kill the processes manually.
echo.
pause 