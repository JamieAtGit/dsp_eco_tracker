#!/bin/bash
# Redis Installation and Enterprise Testing Setup Script

echo "🍺 INSTALLING REDIS ON MACOS"
echo "================================"

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Installing Homebrew first..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew is already installed"
fi

# Install Redis using Homebrew
echo "📦 Installing Redis..."
brew install redis

# Start Redis service
echo "🚀 Starting Redis service..."
brew services start redis

# Wait a moment for Redis to start
sleep 3

# Test Redis connection
echo "🧪 Testing Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running successfully!"
    redis-cli ping
else
    echo "⚠️ Redis may not be fully started yet. Trying manual start..."
    redis-server --daemonize yes
    sleep 2
    
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is now running!"
    else
        echo "❌ Redis startup failed. Please check the installation."
        exit 1
    fi
fi

echo ""
echo "🎯 REDIS INSTALLATION COMPLETE"
echo "================================"
echo "✅ Redis server is running on localhost:6379"
echo "✅ You can now proceed with enterprise feature testing"
echo ""
echo "Next steps:"
echo "1️⃣ Run: python quick_validate_enterprise.py"
echo "2️⃣ Run: python test_enterprise_features.py"
echo "3️⃣ Run: python demo_enterprise_features.py"
echo ""
echo "🚀 Ready for enterprise features testing!"