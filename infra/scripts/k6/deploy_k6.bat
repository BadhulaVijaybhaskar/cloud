@echo off
setlocal enabledelayedexpansion

if "%SIMULATION_MODE%"=="" set SIMULATION_MODE=true
if "%APPROVE_K6_DEPLOY%"=="" set APPROVE_K6_DEPLOY=no
if "%1"=="" (
    set REPORT_DIR=reports\k6
) else (
    set REPORT_DIR=%1
)

if not exist "%REPORT_DIR%" mkdir "%REPORT_DIR%"
set OUT=%REPORT_DIR%\k6_deploy_summary.json

echo K.6 Integration Plane — Deploy (simulation=%SIMULATION_MODE%)

if "%SIMULATION_MODE%"=="false" if not "%APPROVE_K6_DEPLOY%"=="yes" (
    echo ERROR: Live deploy requires APPROVE_K6_DEPLOY=yes
    exit /b 1
)

rem Initialize deploy report
echo { > "%OUT%"
echo   "timestamp": "%date:~10,4%-%date:~4,2%-%date:~7,2%T%time:~0,2%:%time:~3,2%:%time:~6,2%Z", >> "%OUT%"
echo   "simulation_mode": %SIMULATION_MODE%, >> "%OUT%"
echo   "approved": "%APPROVE_K6_DEPLOY%", >> "%OUT%"
echo   "terraform": { >> "%OUT%"
echo     "status": "simulated", >> "%OUT%"
echo     "resources": 3 >> "%OUT%"
echo   }, >> "%OUT%"
echo   "helm": { >> "%OUT%"
echo     "status": "simulated", >> "%OUT%"
echo     "releases": ["k6-integration"] >> "%OUT%"
echo   }, >> "%OUT%"
echo   "summary": { >> "%OUT%"
echo     "overall_status": "DEPLOY_SIMULATED" >> "%OUT%"
echo   } >> "%OUT%"
echo } >> "%OUT%"

echo Deploy simulation complete. Report: %OUT%