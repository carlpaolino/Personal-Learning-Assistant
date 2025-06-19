#!/bin/bash

# PLA - Personalized Learning Assistant Startup Script

echo "🚀 Starting PLA - Personalized Learning Assistant..."

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command_exists redis-cli; then
    echo "⚠️  Redis CLI not found. Make sure Redis is installed and running"
fi

echo "✅ Prerequisites check completed"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Create uploads directory
echo "📁 Creating uploads directory..."
mkdir -p uploads

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating template..."
    cat > .env << EOF
# Database
DATABASE_URL=sqlite:///pla.db
REDIS_URL=redis://localhost:6379/0

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# JWT Secret
JWT_SECRET_KEY=your_super_secret_jwt_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_flask_secret_key_here

# Email Configuration (for reminders)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# File Upload
MAX_FILE_SIZE=20971520
UPLOAD_FOLDER=uploads/
EOF
    echo "📝 Please edit .env file with your configuration"
fi

# Initialize database
echo "🗄️  Initializing database..."
cd backend
export FLASK_APP=run.py
flask db upgrade
cd ..

echo "🎉 Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Start Redis server: redis-server"
echo "3. Run the application: ./run.sh"
echo ""
echo "📚 For more information, see README.md" 