#!/bin/bash

echo "🚀 M-Pesa Statement Analyzer - Fly.io Deployment"
echo "================================================"

echo ""
echo "📋 Pre-deployment checklist:"
echo "✅ Dockerfile created"
echo "✅ fly.toml configured"  
echo "✅ .streamlit/config.toml updated"
echo "✅ JSON config files ready"
echo ""

echo "🔐 Step 1: Login to Fly.io"
fly auth login

echo ""
echo "🚀 Step 2: Launch app"
read -p "Is this your first deployment? (y/n): " choice

if [[ $choice == "y" || $choice == "Y" ]]; then
    echo "🆕 Launching new app..."
    fly launch
else
    echo "📦 Deploying existing app..."
    fly deploy
fi

echo ""
echo "🌐 Opening your deployed app..."
fly open

echo ""
echo "✅ Deployment complete!"
echo "📊 View logs: fly logs"
echo "📈 Check status: fly status"
echo "🔧 Scale app: fly scale memory 1024"