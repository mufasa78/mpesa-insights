@echo off
echo 🚀 M-Pesa Statement Analyzer - Fly.io Deployment
echo ================================================

echo.
echo 📋 Pre-deployment checklist:
echo ✅ Dockerfile created
echo ✅ fly.toml configured  
echo ✅ .streamlit/config.toml updated
echo ✅ JSON config files ready
echo.

echo 🔐 Step 1: Login to Fly.io
fly auth login

echo.
echo 🚀 Step 2: Launch app (first time only)
echo If this is your first deployment, run: fly launch
echo If app already exists, run: fly deploy
echo.

set /p choice="Is this your first deployment? (y/n): "
if /i "%choice%"=="y" (
    echo 🆕 Launching new app...
    fly launch
) else (
    echo 📦 Deploying existing app...
    fly deploy --app mpesa-insights
)

echo.
echo 🌐 Opening your deployed app...
fly open

echo.
echo ✅ Deployment complete!
echo 📊 View logs: fly logs
echo 📈 Check status: fly status
echo 🔧 Scale app: fly scale memory 1024
echo.
pause