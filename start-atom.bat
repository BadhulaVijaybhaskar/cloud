@echo off
echo Starting ATOM - Adaptive Topology Orchestration Module...

cd admin
echo Installing dependencies...
call npm install

echo Starting ATOM Admin UI on port 3001...
call npm run dev

pause