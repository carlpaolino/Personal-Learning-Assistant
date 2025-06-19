#!/usr/bin/env python3
"""
Simple test script to verify PLA application setup
"""
import os
import sys
import requests
import time
from dotenv import load_dotenv

load_dotenv()

def test_backend_setup():
    """Test if backend can be imported and configured"""
    try:
        sys.path.append('backend')
        from app import create_app, db
        from app.models import User, Plan, Task, Upload, Reminder, ChatLog
        
        app = create_app()
        with app.app_context():
            # Test database connection
            db.engine.execute('SELECT 1')
            print("✅ Backend setup successful")
            return True
    except Exception as e:
        print(f"❌ Backend setup failed: {str(e)}")
        return False

def test_frontend_setup():
    """Test if frontend dependencies are installed"""
    try:
        frontend_path = os.path.join('frontend', 'node_modules')
        if os.path.exists(frontend_path):
            print("✅ Frontend dependencies installed")
            return True
        else:
            print("❌ Frontend dependencies not found. Run 'npm install' in frontend directory")
            return False
    except Exception as e:
        print(f"❌ Frontend setup check failed: {str(e)}")
        return False

def test_api_health():
    """Test API health endpoint"""
    try:
        # Start a simple Flask server for testing
        import subprocess
        import threading
        
        def start_server():
            os.environ['FLASK_APP'] = 'backend/run.py'
            subprocess.run(['python', 'backend/run.py'], 
                         capture_output=True, timeout=10)
        
        # Start server in background
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for server to start
        time.sleep(5)
        
        # Test health endpoint
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ API health check successful")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing PLA Application Setup...\n")
    
    tests = [
        ("Backend Setup", test_backend_setup),
        ("Frontend Setup", test_frontend_setup),
        ("API Health", test_api_health)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Testing {name}...")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test failed with exception: {str(e)}")
            results.append((name, False))
        print()
    
    # Summary
    print("📊 Test Results:")
    print("=" * 30)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<15} {status}")
        if not result:
            all_passed = False
    
    print("=" * 30)
    if all_passed:
        print("🎉 All tests passed! Application is ready to run.")
        print("\n📋 To start the application:")
        print("1. Make sure Redis is running: redis-server")
        print("2. Run: ./run.sh")
        print("3. Open: http://localhost:3000")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 