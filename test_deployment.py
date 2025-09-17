#!/usr/bin/env python3
"""
Test script to verify the app can start without errors before deployment.
This helps catch import errors and other issues locally.
"""

import sys
import traceback

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ streamlit")
    except ImportError as e:
        print(f"❌ streamlit: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas")
    except ImportError as e:
        print(f"❌ pandas: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy")
    except ImportError as e:
        print(f"❌ numpy: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ plotly")
    except ImportError as e:
        print(f"❌ plotly: {e}")
        return False
    
    try:
        import pdfplumber
        print("✅ pdfplumber")
    except ImportError as e:
        print(f"❌ pdfplumber: {e}")
        return False
    
    return True

def test_local_modules():
    """Test local module imports"""
    print("\n🔧 Testing local modules...")
    
    modules = [
        'data_processor',
        'categorizer', 
        'visualizer',
        'utils',
        'budget_advisor',
        'expense_predictor',
        'spending_comparator',
        'income_tracker',
        'income_source_manager',
        'feedback_donation_system',
        'markov_predictor',
        'behavior_analyzer'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
        except Exception as e:
            print(f"⚠️ {module}: {e}")
    
    return True

def test_app_startup():
    """Test if the main app can be imported"""
    print("\n🚀 Testing app startup...")
    
    try:
        # This will execute the imports and basic setup
        import app
        print("✅ App imports successful")
        return True
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 M-Pesa Statement Analyzer - Deployment Test")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test local modules
    if not test_local_modules():
        all_passed = False
    
    # Test app startup
    if not test_app_startup():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! App should deploy successfully.")
        print("🚀 You can now run: fly deploy --app mpesa-insights")
    else:
        print("❌ Some tests failed. Fix the issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()