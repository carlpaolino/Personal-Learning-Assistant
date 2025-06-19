#!/usr/bin/env python3
"""
Health check script for PLA application
"""
import os
import sys
import requests
import psycopg2
import redis
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

load_dotenv()

def check_api_health():
    """Check if Flask API is running"""
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Flask API is running")
            return True
        else:
            print(f"❌ Flask API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Flask API is not running: {str(e)}")
        return False

def check_database():
    """Check database connection"""
    try:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///pla.db')
        
        if database_url.startswith('postgresql://'):
            # Parse PostgreSQL URL
            import urllib.parse
            parsed = urllib.parse.urlparse(database_url)
            
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password
            )
            conn.close()
            print("✅ PostgreSQL database connection successful")
        else:
            # SQLite
            import sqlite3
            conn = sqlite3.connect('backend/pla.db')
            conn.close()
            print("✅ SQLite database connection successful")
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def check_redis():
    """Check Redis connection"""
    try:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {str(e)}")
        return False

def check_openai():
    """Check OpenAI API"""
    try:
        from scripts.test_openai import test_openai_connection
        return test_openai_connection()
    except Exception as e:
        print(f"❌ OpenAI API check failed: {str(e)}")
        return False

def main():
    """Run all health checks"""
    print("🔍 Running PLA Health Checks...\n")
    
    checks = [
        ("Flask API", check_api_health),
        ("Database", check_database),
        ("Redis", check_redis),
        ("OpenAI API", check_openai)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"Checking {name}...")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with exception: {str(e)}")
            results.append((name, False))
        print()
    
    # Summary
    print("📊 Health Check Summary:")
    print("=" * 40)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<15} {status}")
        if not result:
            all_passed = False
    
    print("=" * 40)
    if all_passed:
        print("🎉 All health checks passed!")
        return 0
    else:
        print("⚠️  Some health checks failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 