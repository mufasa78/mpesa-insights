"""
Test script for the feedback and donation system
"""

import json
import os
from feedback_donation_system import FeedbackDonationSystem

def test_feedback_system():
    """Test the feedback system functionality"""
    print("🧪 Testing Feedback & Donation System")
    print("=" * 50)
    
    # Initialize system
    system = FeedbackDonationSystem()
    
    # Test 1: Configuration loading
    print("1. Testing configuration loading...")
    config = system.donation_config
    print(f"   ✅ Config loaded: {len(config)} settings")
    print(f"   📱 M-Pesa Paybill: {config.get('mpesa_paybill', 'Not set')}")
    print(f"   ☕ Buy Me Coffee: {config.get('buy_me_coffee_url', 'Not set')}")
    
    # Test 2: Feedback data structure
    print("\n2. Testing feedback data structure...")
    test_feedback = {
        "type": "Feature Request",
        "rating": 5,
        "name": "Test User",
        "email": "test@example.com",
        "feedback": "This is a test feedback entry",
        "features_used": ["Dashboard", "Budget Analysis"],
        "most_valuable": "Dashboard",
        "improvements": "Add more charts",
        "technical_info": {
            "browser": "Chrome 91",
            "device": "Windows 10",
            "file_size": "2MB"
        }
    }
    
    # Save test feedback
    system.save_feedback(test_feedback)
    print("   ✅ Test feedback saved successfully")
    
    # Load and verify
    feedback_data = system.load_feedback_data()
    print(f"   ✅ Feedback loaded: {len(feedback_data)} entries")
    
    if feedback_data:
        latest = feedback_data[-1]
        print(f"   📝 Latest feedback: {latest['type']} - {latest['rating']}⭐")
        print(f"   👤 From: {latest['name']}")
        print(f"   🕒 Timestamp: {latest['timestamp']}")
    
    # Test 3: Configuration validation
    print("\n3. Testing configuration validation...")
    required_fields = ['buy_me_coffee_url', 'mpesa_paybill', 'mpesa_account', 'github_repo']
    
    for field in required_fields:
        value = config.get(field, '')
        status = "✅" if value and value != "Not set" else "⚠️"
        print(f"   {status} {field}: {value or 'Not configured'}")
    
    # Test 4: File structure
    print("\n4. Testing file structure...")
    files_to_check = [
        'feedback_donation_system.py',
        'donation_config.json',
        'admin_feedback.py',
        'user_feedback.json'
    ]
    
    for file in files_to_check:
        exists = os.path.exists(file)
        status = "✅" if exists else "❌"
        print(f"   {status} {file}: {'Found' if exists else 'Missing'}")
    
    print("\n" + "=" * 50)
    print("🎉 Feedback system test completed!")
    
    # Cleanup test data (optional)
    cleanup = input("\n🗑️ Remove test feedback data? (y/n): ").lower().strip()
    if cleanup == 'y':
        if os.path.exists('user_feedback.json'):
            # Remove only test entries
            feedback_data = system.load_feedback_data()
            cleaned_data = [f for f in feedback_data if f.get('name') != 'Test User']
            
            with open('user_feedback.json', 'w') as f:
                json.dump(cleaned_data, f, indent=2)
            
            print("   ✅ Test data cleaned up")
        else:
            print("   ℹ️ No test data to clean")

if __name__ == "__main__":
    test_feedback_system()