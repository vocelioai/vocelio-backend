@echo off
echo Deploying remaining Vocelio services to Railway
echo ================================================

set services=agents agent-store billing-pro call-center voice-lab voice-marketplace flow-builder integrations settings developer-api compliance white-label

for %%s in (%services%) do (
    echo.
    echo [Deploying %%s]
    cd apps/%%s
    echo Adding service %%s...
    railway add --service %%s
    echo Deploying %%s...
    railway up --detach
    echo Waiting 10 seconds...
    timeout /t 10 /nobreak >nul
    cd ../../
)

echo.
echo ================================================
echo All services deployment attempted!
echo Check Railway dashboard for status.
