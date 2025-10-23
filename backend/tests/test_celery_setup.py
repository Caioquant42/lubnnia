#!/usr/bin/env python3
"""
Test script to verify Celery configuration is working properly
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_celery_import():
    """Test if we can import celery from our app"""
    try:
        from celery_worker import celery
        print("✓ Successfully imported celery from celery_worker")
        return True
    except Exception as e:
        print(f"✗ Failed to import celery: {e}")
        return False

def test_celery_config():
    """Test celery configuration"""
    try:
        from celery_worker import celery
        
        print("\n=== Celery Configuration ===")
        print(f"Broker URL: {celery.conf.broker_url}")
        print(f"Result Backend: {celery.conf.result_backend}")
        print(f"Timezone: {celery.conf.timezone}")
        print(f"Beat Schedule Tasks: {len(celery.conf.beat_schedule) if celery.conf.beat_schedule else 0}")
        
        if celery.conf.beat_schedule:
            print("\n=== Scheduled Tasks ===")
            for task_name, task_config in celery.conf.beat_schedule.items():
                print(f"- {task_name}: {task_config['task']}")
                print(f"  Schedule: {task_config['schedule']}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to check celery config: {e}")
        return False

def test_task_import():
    """Test if we can import tasks"""
    try:
        from app import tasks
        print("✓ Successfully imported tasks module")
        
        # List available tasks
        task_functions = [attr for attr in dir(tasks) if callable(getattr(tasks, attr)) and not attr.startswith('_')]
        print(f"Available tasks: {len(task_functions)}")
        for task in task_functions:
            print(f"  - {task}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to import tasks: {e}")
        return False

def test_flask_app():
    """Test Flask app creation"""
    try:
        from app import create_app
        flask_app, celery_app = create_app()
        print("✓ Successfully created Flask app and Celery instance")
        print(f"Flask app name: {flask_app.name}")
        print(f"Celery app name: {celery_app.main}")
        return True
    except Exception as e:
        print(f"✗ Failed to create Flask app: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Celery Setup...\n")
    
    tests = [
        ("Celery Import", test_celery_import),
        ("Flask App Creation", test_flask_app),
        ("Celery Configuration", test_celery_config),
        ("Task Import", test_task_import),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🎉 All tests passed! Celery setup is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
