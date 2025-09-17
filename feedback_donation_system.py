"""
Feedback and Donation System for M-Pesa Statement Analyzer
Handles user feedback collection and donation options (Buy Me a Coffee & M-Pesa)
"""

import streamlit as st
import json
import os
from datetime import datetime
import requests
from typing import Dict, List, Optional

class FeedbackDonationSystem:
    def __init__(self):
        self.feedback_file = "user_feedback.json"
        self.donation_config_file = "donation_config.json"
        self.load_donation_config()
    
    def load_donation_config(self):
        """Load donation configuration"""
        default_config = {
            "buy_me_coffee_url": "https://buymeacoffee.com/njorogesta0",
            "mpesa_phone": "0716131888",
            "project_name": "M-Pesa Statement Analyzer",
            "github_repo": "https://github.com/yourusername/mpesa-analyzer"
        }
        
        try:
            with open(self.donation_config_file, 'r') as f:
                self.donation_config = json.load(f)
        except FileNotFoundError:
            self.donation_config = default_config
            self.save_donation_config()
    
    def save_donation_config(self):
        """Save donation configuration"""
        with open(self.donation_config_file, 'w') as f:
            json.dump(self.donation_config, f, indent=2)
    
    def load_feedback_data(self) -> List[Dict]:
        """Load existing feedback data"""
        try:
            with open(self.feedback_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_feedback(self, feedback_data: Dict):
        """Save new feedback"""
        feedback_list = self.load_feedback_data()
        feedback_data['timestamp'] = datetime.now().isoformat()
        feedback_data['id'] = len(feedback_list) + 1
        feedback_list.append(feedback_data)
        
        with open(self.feedback_file, 'w') as f:
            json.dump(feedback_list, f, indent=2)
    
    def render_donation_section(self):
        """Render the donation section"""
        st.markdown("---")
        st.header("☕ Support This Project")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌍 International Donations")
            st.markdown(f"""
            **Buy Me a Coffee** ☕
            
            If this app helped you manage your finances better, consider buying me a coffee!
            Your support helps keep this project free and open-source.
            """)
            
            # Buy Me a Coffee button
            buy_me_coffee_url = self.donation_config.get("buy_me_coffee_url", "#")
            st.markdown(f"""
            <a href="{buy_me_coffee_url}" target="_blank">
                <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" 
                     alt="Buy Me A Coffee" 
                     style="height: 60px !important;width: 217px !important;" >
            </a>
            """, unsafe_allow_html=True)
            
            st.markdown("**Other Options:**")
            st.markdown("• PayPal: [Donate via PayPal](https://paypal.me/yourhandle)")
            st.markdown("• Ko-fi: [Support on Ko-fi](https://ko-fi.com/yourhandle)")
        
        with col2:
            st.subheader("🇰🇪 M-Pesa Donations (Kenya)")
            
            mpesa_phone = self.donation_config.get("mpesa_phone", "0716131888")
            
            st.markdown(f"""
            **M-Pesa Send Money** 💸
            
            • **Phone Number:** `{mpesa_phone}`
            
            **How to donate via M-Pesa:**
            1. Go to M-Pesa menu → Send Money
            2. Enter Phone Number: `{mpesa_phone}`
            3. Enter your donation amount
            4. Enter PIN → Send
            
            **Simple and direct!** 🎯
            """)
            
            # QR Code placeholder (you can generate actual QR codes)
            st.info("💡 **Tip:** Save these numbers in your M-Pesa contacts for easy future donations!")
        
        # Donation impact
        st.subheader("💝 Your Impact")
        
        impact_col1, impact_col2, impact_col3 = st.columns(3)
        
        with impact_col1:
            st.markdown("""
            **KSh 50 - 200** ☕
            
            • Shows appreciation
            • Motivates development
            • Covers basic costs
            """)
        
        with impact_col2:
            st.markdown("""
            **KSh 200 - 1,000** 🚀
            
            • Funds new features
            • Improves performance
            • Better hosting
            """)
        
        with impact_col3:
            st.markdown("""
            **KSh 1,000+** 🌟
            
            • Major feature development
            • Premium infrastructure
            • Dedicated support
            """)
        
        # Thank you message
        st.success("""
        🙏 **Thank you for considering a donation!** 
        
        Every contribution, no matter the size, helps keep this project alive and free for everyone. 
        Your support enables continuous improvements and new features that benefit the entire community.
        """)
    
    def render_feedback_form(self):
        """Render the feedback collection form"""
        st.header("📝 Share Your Feedback")
        
        st.markdown("""
        Your feedback helps improve this app for everyone! Please share your experience, 
        suggestions, or report any issues you've encountered.
        """)
        
        with st.form("feedback_form"):
            # Feedback type
            feedback_type = st.selectbox(
                "Feedback Type",
                ["General Feedback", "Bug Report", "Feature Request", "User Experience", "Performance Issue"]
            )
            
            # Rating
            rating = st.select_slider(
                "Overall Rating",
                options=[1, 2, 3, 4, 5],
                value=4,
                format_func=lambda x: "⭐" * x
            )
            
            # User info (optional)
            col1, col2 = st.columns(2)
            with col1:
                user_name = st.text_input("Name (Optional)", placeholder="Your name")
            with col2:
                user_email = st.text_input("Email (Optional)", placeholder="your.email@example.com")
            
            # Main feedback
            feedback_text = st.text_area(
                "Your Feedback",
                placeholder="Please share your thoughts, suggestions, or describe any issues...",
                height=150
            )
            
            # Feature usage
            st.subheader("📊 Feature Usage")
            features_used = st.multiselect(
                "Which features have you used?",
                [
                    "PDF Upload & Processing",
                    "Expense Categorization", 
                    "Financial Dashboard",
                    "Budget Analysis",
                    "Income Tracking",
                    "Spending Comparisons",
                    "AI Predictions",
                    "Markov Chain Analysis",
                    "Data Export"
                ]
            )
            
            # Most valuable feature
            most_valuable = st.selectbox(
                "Most Valuable Feature",
                [""] + [
                    "PDF Upload & Processing",
                    "Expense Categorization", 
                    "Financial Dashboard",
                    "Budget Analysis",
                    "Income Tracking",
                    "Spending Comparisons",
                    "AI Predictions",
                    "Markov Chain Analysis",
                    "Data Export"
                ]
            )
            
            # Improvement suggestions
            improvements = st.text_area(
                "Suggested Improvements",
                placeholder="What features would you like to see added or improved?",
                height=100
            )
            
            # Technical info
            with st.expander("🔧 Technical Information (Optional)"):
                browser = st.text_input("Browser", placeholder="e.g., Chrome 91, Safari 14")
                device = st.text_input("Device", placeholder="e.g., Windows 10, MacBook Pro, Android")
                file_size = st.text_input("PDF File Size", placeholder="e.g., 2MB, 500KB")
            
            # Submit button
            submitted = st.form_submit_button("📤 Submit Feedback", type="primary")
            
            if submitted:
                if feedback_text.strip():
                    feedback_data = {
                        "type": feedback_type,
                        "rating": rating,
                        "name": user_name if user_name.strip() else "Anonymous",
                        "email": user_email if user_email.strip() else None,
                        "feedback": feedback_text,
                        "features_used": features_used,
                        "most_valuable": most_valuable,
                        "improvements": improvements,
                        "technical_info": {
                            "browser": browser,
                            "device": device,
                            "file_size": file_size
                        }
                    }
                    
                    self.save_feedback(feedback_data)
                    
                    st.success("🎉 Thank you for your feedback! Your input helps make this app better.")
                    
                    # Show appreciation message
                    if rating >= 4:
                        st.balloons()
                        st.markdown("### 🌟 We're thrilled you're enjoying the app!")
                        st.markdown("Consider supporting the project with a small donation to help us keep improving it.")
                    
                    # Auto-rerun to clear form
                    st.rerun()
                else:
                    st.error("Please provide some feedback before submitting.")
    
    def render_feedback_stats(self):
        """Render feedback statistics (for admin/developer view)"""
        feedback_data = self.load_feedback_data()
        
        if not feedback_data:
            st.info("No feedback received yet.")
            return
        
        st.subheader("📊 Feedback Statistics")
        
        # Basic stats
        total_feedback = len(feedback_data)
        avg_rating = sum(f.get('rating', 0) for f in feedback_data) / total_feedback if total_feedback > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Feedback", total_feedback)
        
        with col2:
            st.metric("Average Rating", f"{avg_rating:.1f} ⭐")
        
        with col3:
            recent_feedback = len([f for f in feedback_data if 
                                 datetime.fromisoformat(f['timestamp']).date() >= 
                                 (datetime.now().date() - timedelta(days=7))])
            st.metric("This Week", recent_feedback)
        
        # Rating distribution
        rating_counts = {}
        for f in feedback_data:
            rating = f.get('rating', 0)
            rating_counts[rating] = rating_counts.get(rating, 0) + 1
        
        st.subheader("⭐ Rating Distribution")
        for rating in sorted(rating_counts.keys(), reverse=True):
            count = rating_counts[rating]
            percentage = (count / total_feedback) * 100
            st.write(f"{'⭐' * rating} ({rating}): {count} ({percentage:.1f}%)")
        
        # Feature usage
        feature_usage = {}
        for f in feedback_data:
            for feature in f.get('features_used', []):
                feature_usage[feature] = feature_usage.get(feature, 0) + 1
        
        if feature_usage:
            st.subheader("📈 Feature Usage")
            sorted_features = sorted(feature_usage.items(), key=lambda x: x[1], reverse=True)
            for feature, count in sorted_features:
                percentage = (count / total_feedback) * 100
                st.write(f"• **{feature}**: {count} users ({percentage:.1f}%)")
    
    def render_github_promotion(self):
        """Render GitHub repository promotion"""
        st.markdown("---")
        st.header("🚀 Open Source Project")
        
        github_url = self.donation_config.get("github_repo", "#")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            ### 🌟 Star us on GitHub!
            
            This project is **100% open source** and available on GitHub. 
            
            **Why open source?**
            • 🔒 **Transparency**: You can see exactly how your data is processed
            • 🛡️ **Security**: Community-reviewed code you can trust
            • 🤝 **Community**: Contribute features and improvements
            • 📚 **Learning**: Study the code and learn from it
            
            **How you can contribute:**
            • ⭐ Star the repository
            • 🐛 Report bugs and issues
            • 💡 Suggest new features
            • 🔧 Submit pull requests
            • 📖 Improve documentation
            """)
        
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <a href="{github_url}" target="_blank" style="text-decoration: none;">
                    <div style="background: #24292e; color: white; padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <h3 style="margin: 0; color: white;">🐙 GitHub</h3>
                        <p style="margin: 5px 0; color: #f6f8fa;">View Source Code</p>
                    </div>
                </a>
                
                <a href="{github_url}/issues" target="_blank" style="text-decoration: none;">
                    <div style="background: #28a745; color: white; padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <h3 style="margin: 0; color: white;">🐛 Issues</h3>
                        <p style="margin: 5px 0; color: white;">Report Bugs</p>
                    </div>
                </a>
                
                <a href="{github_url}/discussions" target="_blank" style="text-decoration: none;">
                    <div style="background: #6f42c1; color: white; padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <h3 style="margin: 0; color: white;">💬 Discuss</h3>
                        <p style="margin: 5px 0; color: white;">Join Community</p>
                    </div>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        # Community stats (placeholder - you can integrate with GitHub API)
        st.subheader("📊 Community Stats")
        
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        
        with stats_col1:
            st.metric("⭐ Stars", "0", help="GitHub stars")
        
        with stats_col2:
            st.metric("🍴 Forks", "0", help="Repository forks")
        
        with stats_col3:
            st.metric("🐛 Issues", "0", help="Open issues")
        
        with stats_col4:
            st.metric("👥 Contributors", "1", help="Active contributors")
    
    def render_privacy_trust_section(self):
        """Render privacy and trust information"""
        st.markdown("---")
        st.header("🔒 Privacy & Trust")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🛡️ Your Data is Safe")
            st.markdown("""
            **Local Processing Only**
            • Your M-Pesa data never leaves your device
            • All analysis happens in your browser
            • No data is sent to external servers
            • No account registration required
            
            **Open Source Transparency**
            • Full source code available on GitHub
            • Community-reviewed security
            • No hidden data collection
            • You can audit the code yourself
            """)
        
        with col2:
            st.subheader("🤝 Why Trust This App?")
            st.markdown("""
            **Built for the Community**
            • Created by developers who understand privacy
            • No venture capital or corporate interests
            • Donation-supported, not ad-supported
            • Community-driven development
            
            **Technical Safeguards**
            • Client-side processing only
            • No external API calls for data
            • Secure file handling
            • Regular security updates
            """)
        
        # Trust indicators
        st.subheader("✅ Trust Indicators")
        
        trust_col1, trust_col2, trust_col3 = st.columns(3)
        
        with trust_col1:
            st.markdown("""
            **🔓 Open Source**
            
            Complete transparency
            Community oversight
            Auditable code
            """)
        
        with trust_col2:
            st.markdown("""
            **🏠 Local Processing**
            
            Data stays on your device
            No cloud uploads
            Offline capable
            """)
        
        with trust_col3:
            st.markdown("""
            **🤝 Community Driven**
            
            User feedback driven
            No corporate agenda
            Donation supported
            """)
    
    def render_complete_support_section(self):
        """Render the complete support section with feedback, donations, and community"""
        st.title("💝 Support & Community")
        
        # Create tabs for different sections
        support_tab1, support_tab2, support_tab3, support_tab4 = st.tabs([
            "📝 Feedback", "☕ Donate", "🚀 GitHub", "🔒 Privacy"
        ])
        
        with support_tab1:
            self.render_feedback_form()
        
        with support_tab2:
            self.render_donation_section()
        
        with support_tab3:
            self.render_github_promotion()
        
        with support_tab4:
            self.render_privacy_trust_section()
    
    def render_quick_support_sidebar(self):
        """Render a quick support section in the sidebar"""
        with st.sidebar:
            st.markdown("---")
            st.subheader("💝 Support This Project")
            
            # Quick donation buttons
            buy_me_coffee_url = self.donation_config.get("buy_me_coffee_url", "#")
            
            st.markdown(f"""
            <div style="text-align: center;">
                <a href="{buy_me_coffee_url}" target="_blank">
                    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" 
                         alt="Buy Me A Coffee" 
                         style="height: 40px !important;width: 145px !important;" >
                </a>
            </div>
            """, unsafe_allow_html=True)
            
            # M-Pesa quick info
            mpesa_phone = self.donation_config.get("mpesa_phone", "0716131888")
            st.markdown(f"""
            **M-Pesa Send Money:**
            📱 `{mpesa_phone}`
            """)
            
            # Quick feedback
            if st.button("📝 Give Feedback", use_container_width=True):
                st.session_state.show_feedback = True
            
            # GitHub link
            github_url = self.donation_config.get("github_repo", "#")
            st.markdown(f"""
            <div style="text-align: center; margin-top: 10px;">
                <a href="{github_url}" target="_blank" style="text-decoration: none;">
                    <div style="background: #24292e; color: white; padding: 10px; border-radius: 5px;">
                        🐙 View on GitHub
                    </div>
                </a>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.caption("🔒 Your data stays private - processed locally only")

# Configuration helper function
def setup_donation_config():
    """Helper function to set up donation configuration"""
    st.header("⚙️ Configure Donation Settings")
    
    system = FeedbackDonationSystem()
    config = system.donation_config
    
    with st.form("donation_config"):
        st.subheader("☕ Buy Me a Coffee")
        buy_me_coffee = st.text_input(
            "Buy Me a Coffee URL",
            value=config.get("buy_me_coffee_url", ""),
            placeholder="https://buymeacoffee.com/yourhandle"
        )
        
        st.subheader("📱 M-Pesa Settings")
        mpesa_phone = st.text_input(
            "M-Pesa Phone Number",
            value=config.get("mpesa_phone", ""),
            placeholder="0716131888"
        )
        
        st.subheader("🚀 Project Settings")
        project_name = st.text_input(
            "Project Name",
            value=config.get("project_name", "M-Pesa Statement Analyzer")
        )
        
        github_repo = st.text_input(
            "GitHub Repository URL",
            value=config.get("github_repo", ""),
            placeholder="https://github.com/yourusername/mpesa-analyzer"
        )
        
        if st.form_submit_button("💾 Save Configuration"):
            new_config = {
                "buy_me_coffee_url": buy_me_coffee,
                "mpesa_phone": mpesa_phone,
                "project_name": project_name,
                "github_repo": github_repo
            }
            
            system.donation_config = new_config
            system.save_donation_config()
            
            st.success("✅ Configuration saved successfully!")
            st.rerun()