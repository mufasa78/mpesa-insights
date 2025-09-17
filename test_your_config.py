"""
Test the updated donation configuration
"""

from feedback_donation_system import FeedbackDonationSystem

def test_config():
    print("🧪 Testing Your Donation Configuration")
    print("=" * 50)
    
    system = FeedbackDonationSystem()
    config = system.donation_config
    
    print("✅ Configuration loaded successfully!")
    print()
    print("📋 Your Donation Details:")
    print(f"☕ Buy Me Coffee: {config.get('buy_me_coffee_url')}")
    print(f"📱 M-Pesa Phone: {config.get('mpesa_phone')}")
    print(f"🚀 Project: {config.get('project_name')}")
    print()
    
    # Validate URLs
    buy_me_coffee = config.get('buy_me_coffee_url', '')
    if 'njorogesta0' in buy_me_coffee:
        print("✅ Buy Me Coffee URL looks correct!")
    else:
        print("⚠️ Buy Me Coffee URL might need checking")
    
    # Validate phone
    phone = config.get('mpesa_phone', '')
    if phone.startswith('07') and len(phone) == 10:
        print("✅ M-Pesa phone number format looks good!")
    else:
        print("⚠️ M-Pesa phone number format might need checking")
    
    print()
    print("🎉 Ready to collect donations!")
    print()
    print("💡 Next steps:")
    print("1. Update GitHub repo URL when you create the repository")
    print("2. Test the app locally: streamlit run app.py")
    print("3. Deploy to Streamlit Cloud")
    print("4. Share with friends and start collecting feedback!")

if __name__ == "__main__":
    test_config()