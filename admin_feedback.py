"""
Admin interface for viewing feedback and managing donations
Run this separately to view collected feedback
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
from feedback_donation_system import FeedbackDonationSystem, setup_donation_config

st.set_page_config(
    page_title="Admin - Feedback & Donations",
    page_icon="⚙️",
    layout="wide"
)

def main():
    st.title("⚙️ Admin Dashboard - Feedback & Donations")
    
    # Initialize system
    feedback_system = FeedbackDonationSystem()
    
    # Sidebar navigation
    with st.sidebar:
        st.header("🔧 Admin Tools")
        admin_section = st.selectbox(
            "Select Section",
            ["📊 Feedback Analytics", "⚙️ Donation Config", "📝 Raw Feedback Data"]
        )
    
    if admin_section == "📊 Feedback Analytics":
        st.header("📊 Feedback Analytics")
        feedback_system.render_feedback_stats()
        
        # Detailed feedback view
        feedback_data = feedback_system.load_feedback_data()
        
        if feedback_data:
            st.subheader("📝 Recent Feedback")
            
            # Convert to DataFrame for better display
            df_feedback = pd.DataFrame(feedback_data)
            
            # Sort by timestamp (most recent first)
            df_feedback['timestamp'] = pd.to_datetime(df_feedback['timestamp'])
            df_feedback = df_feedback.sort_values('timestamp', ascending=False)
            
            # Display recent feedback
            for _, feedback in df_feedback.head(10).iterrows():
                with st.expander(f"⭐ {feedback['rating']}/5 - {feedback['type']} ({feedback['timestamp'].strftime('%Y-%m-%d %H:%M')})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Name:** {feedback['name']}")
                        st.write(f"**Email:** {feedback.get('email', 'Not provided')}")
                        st.write(f"**Rating:** {'⭐' * feedback['rating']}")
                        st.write(f"**Type:** {feedback['type']}")
                    
                    with col2:
                        if feedback.get('features_used'):
                            st.write(f"**Features Used:** {', '.join(feedback['features_used'])}")
                        if feedback.get('most_valuable'):
                            st.write(f"**Most Valuable:** {feedback['most_valuable']}")
                    
                    st.write(f"**Feedback:** {feedback['feedback']}")
                    
                    if feedback.get('improvements'):
                        st.write(f"**Improvements:** {feedback['improvements']}")
                    
                    # Technical info
                    tech_info = feedback.get('technical_info', {})
                    if any(tech_info.values()):
                        st.write("**Technical Info:**")
                        for key, value in tech_info.items():
                            if value:
                                st.write(f"  • {key.title()}: {value}")
    
    elif admin_section == "⚙️ Donation Config":
        st.header("⚙️ Donation Configuration")
        setup_donation_config()
        
        # Current configuration display
        st.subheader("📋 Current Configuration")
        config = feedback_system.donation_config
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Buy Me a Coffee:**")
            st.code(config.get("buy_me_coffee_url", "Not set"))
            

        
        with col2:
            st.write("**M-Pesa Phone:**")
            st.code(config.get("mpesa_phone", "Not set"))
            
            st.write("**Project Name:**")
            st.code(config.get("project_name", "Not set"))
            
            st.write("**GitHub Repo:**")
            st.code(config.get("github_repo", "Not set"))
    
    elif admin_section == "📝 Raw Feedback Data":
        st.header("📝 Raw Feedback Data")
        
        feedback_data = feedback_system.load_feedback_data()
        
        if feedback_data:
            # Convert to DataFrame
            df_feedback = pd.DataFrame(feedback_data)
            df_feedback['timestamp'] = pd.to_datetime(df_feedback['timestamp'])
            
            # Display options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                show_count = st.selectbox("Show entries", [10, 25, 50, 100, "All"])
            
            with col2:
                sort_by = st.selectbox("Sort by", ["timestamp", "rating", "type"])
            
            with col3:
                sort_order = st.selectbox("Order", ["Descending", "Ascending"])
            
            # Apply sorting
            ascending = sort_order == "Ascending"
            df_feedback = df_feedback.sort_values(sort_by, ascending=ascending)
            
            # Apply count limit
            if show_count != "All":
                df_feedback = df_feedback.head(show_count)
            
            # Display data
            st.dataframe(df_feedback, use_container_width=True)
            
            # Export options
            st.subheader("📤 Export Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Download as CSV"):
                    csv = df_feedback.to_csv(index=False)
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv,
                        file_name=f"feedback_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("📋 Download as JSON"):
                    json_data = df_feedback.to_json(orient='records', date_format='iso')
                    st.download_button(
                        label="💾 Download JSON",
                        data=json_data,
                        file_name=f"feedback_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        else:
            st.info("No feedback data available yet.")
    
    # Footer
    st.markdown("---")
    st.caption("🔒 Admin Dashboard - Handle user data responsibly")

if __name__ == "__main__":
    main()