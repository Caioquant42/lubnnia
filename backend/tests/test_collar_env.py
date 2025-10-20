#!/usr/bin/env python3

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.utils.collar import OPLAB_TOKEN, headers
    print("✅ Successfully loaded OPLAB_TOKEN from .env file")
    print(f"Token starts with: {OPLAB_TOKEN[:10]}..." if OPLAB_TOKEN else "❌ Token is None")
    print(f"Headers configured: {headers}")
    print("✅ collar.py environment configuration working correctly!")
except Exception as e:
    print(f"❌ Error loading collar.py: {str(e)}")
    sys.exit(1)
