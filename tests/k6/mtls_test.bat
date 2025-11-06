@echo off
setlocal enabledelayedexpansion

if "%1"=="" (
    set REPORT_DIR=reports\k6
) else (
    set REPORT_DIR=%1
)

if not exist "%REPORT_DIR%" mkdir "%REPORT_DIR%"
set OUT=%REPORT_DIR%\mtls_handshake.json

echo {"checks": [ > "%OUT%"
echo   {"host":"localhost","port":8901,"status":"simulated","rc":0,"snippet":"Simulated mTLS handshake - connection would be verified in live mode"} >> "%OUT%"
echo ]} >> "%OUT%"

echo Wrote %OUT%