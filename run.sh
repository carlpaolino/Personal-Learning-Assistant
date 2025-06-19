#!/bin/bash

# PLA - Personalized Learning Assistant Run Script

echo "🚀 Starting PLA - Personalized Learning Assistant..."

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Function to cleanup background processes
cleanup() {
    echo "🛑 Stopping all services..."
    kill $FLASK_PID $CELERY_PID $CELERY_BEAT_PID $REACT_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start Flask API
echo "🌐 Starting Flask API..."
cd backend
export FLASK_APP=run.py
export FLASK_ENV=development
python run.py &
FLASK_PID=$!
cd ..

# Wait a moment for Flask to start
sleep 3

# Start Celery worker
echo "⚙️  Starting Celery worker..."
cd backend
celery -A app.celery worker --loglevel=info &
CELERY_PID=$!
cd ..

# Start Celery beat
echo "⏰ Starting Celery beat..."
cd backend
celery -A app.celery beat --loglevel=info &
CELERY_BEAT_PID=$!
cd ..

# Start React frontend
echo "🎨 Starting React frontend..."
cd frontend
npm start &
REACT_PID=$!
cd ..

echo "✅ All services started!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5000"
echo "📊 API Health: http://localhost:5000/api/health"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for all background processes
wait 