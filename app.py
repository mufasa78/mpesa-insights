import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import io

from data_processor import DataProcessor
from categorizer import ExpenseCategorizer
from visualizer import create_pie_chart, create_bar_chart, create_trend_chart, create_monthly_comparison
from utils import export_to_csv, export_summary_to_pdf

# Page configuration
st.set_page_config(
    page_title="M-Pesa Statement Analyzer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'categorized_data' not in st.session_state:
    st.session_state.categorized_data = None
if 'category_mappings' not in st.session_state:
    st.session_state.category_mappings = {}

def load_category_mappings():
    """Load existing category mappings from JSON file"""
    try:
        with open('category_mappings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_category_mappings(mappings):
    """Save category mappings to JSON file"""
    with open('category_mappings.json', 'w') as f:
        json.dump(mappings, f, indent=2)

def main():
    st.title("💰 M-Pesa Statement Analyzer")
    st.markdown("**Analyze your M-Pesa transactions and gain insights into your spending patterns**")
    
    # Load existing category mappings
    st.session_state.category_mappings = load_category_mappings()
    
    # Initialize components
    processor = DataProcessor()
    categorizer = ExpenseCategorizer(st.session_state.category_mappings)
    
    # Sidebar for file upload and filters
    with st.sidebar:
        st.header("📁 Upload Statement")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose your M-Pesa statement file",
            type=['csv', 'pdf'],
            help="Upload CSV or PDF format M-Pesa statements"
        )
        
        if uploaded_file is not None:
            with st.spinner("Processing statement..."):
                try:
                    # Process the uploaded file
                    if uploaded_file.type == "application/pdf":
                        df = processor.process_pdf(uploaded_file)
                    else:
                        df = processor.process_csv(uploaded_file)
                    
                    if df is not None and not df.empty:
                        st.session_state.processed_data = df
                        
                        # Categorize transactions
                        categorized_df = categorizer.categorize_transactions(df)
                        st.session_state.categorized_data = categorized_df
                        
                        st.success(f"✅ Processed {len(df)} transactions")
                    else:
                        st.error("❌ No valid transactions found in the file")
                        
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
        
        # Filters section
        if st.session_state.categorized_data is not None:
            st.header("🔍 Filters")
            df = st.session_state.categorized_data
            
            # Date range filter
            if 'Date' in df.columns:
                min_date = df['Date'].min().date()
                max_date = df['Date'].max().date()
                
                date_range = st.date_input(
                    "Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
                
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
            
            # Category filter
            categories = df['Category'].unique().tolist()
            selected_categories = st.multiselect(
                "Categories",
                categories,
                default=categories
            )
            df = df[df['Category'].isin(selected_categories)]
            
            # Transaction type filter
            if 'Type' in df.columns:
                transaction_types = df['Type'].unique().tolist()
                selected_types = st.multiselect(
                    "Transaction Types",
                    transaction_types,
                    default=transaction_types
                )
                df = df[df['Type'].isin(selected_types)]
            
            # Amount range filter
            if 'Amount' in df.columns:
                min_amount = float(df['Amount'].min())
                max_amount = float(df['Amount'].max())
                
                amount_range = st.slider(
                    "Amount Range (KSh)",
                    min_value=min_amount,
                    max_value=max_amount,
                    value=(min_amount, max_amount)
                )
                
                df = df[(df['Amount'] >= amount_range[0]) & (df['Amount'] <= amount_range[1])]
            
            # Update filtered data
            st.session_state.filtered_data = df
    
    # Main content area
    if st.session_state.categorized_data is not None:
        # Use filtered data if available, otherwise use all categorized data
        df = st.session_state.get('filtered_data', st.session_state.categorized_data)
        
        if df.empty:
            st.warning("⚠️ No transactions match the current filters")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_transactions = len(df)
            st.metric("Total Transactions", total_transactions)
        
        with col2:
            total_spent = df[df['Amount'] < 0]['Amount'].sum() * -1
            st.metric("Total Spent", f"KSh {total_spent:,.2f}")
        
        with col3:
            total_received = df[df['Amount'] > 0]['Amount'].sum()
            st.metric("Total Received", f"KSh {total_received:,.2f}")
        
        with col4:
            net_amount = df['Amount'].sum()
            st.metric("Net Amount", f"KSh {net_amount:,.2f}")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📈 Trends", "💡 Insights", "⚙️ Categories", "📥 Export"])
        
        with tab1:
            st.subheader("Expense Breakdown")
            
            # Filter for expenses only (negative amounts)
            expenses_df = df[df['Amount'] < 0].copy()
            expenses_df['Amount'] = expenses_df['Amount'] * -1  # Convert to positive for display
            
            if not expenses_df.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Pie chart for category breakdown
                    category_totals = expenses_df.groupby('Category')['Amount'].sum().reset_index()
                    fig_pie = create_pie_chart(category_totals, 'Category', 'Amount', 'Expense Categories')
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    # Bar chart for top categories
                    top_categories = category_totals.nlargest(10, 'Amount')
                    fig_bar = create_bar_chart(top_categories, 'Category', 'Amount', 'Top 10 Categories')
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # Detailed breakdown table
                st.subheader("Category Summary")
                category_summary = expenses_df.groupby('Category').agg({
                    'Amount': ['sum', 'count', 'mean']
                }).round(2)
                category_summary.columns = ['Total (KSh)', 'Transactions', 'Average (KSh)']
                category_summary = category_summary.sort_values('Total (KSh)', ascending=False)
                
                # Add percentage column
                total_expenses = category_summary['Total (KSh)'].sum()
                category_summary['Percentage'] = (category_summary['Total (KSh)'] / total_expenses * 100).round(1)
                
                st.dataframe(category_summary, use_container_width=True)
            else:
                st.info("No expense transactions found in the selected data")
        
        with tab2:
            st.subheader("Spending Trends")
            
            expenses_df = df[df['Amount'] < 0].copy()
            expenses_df['Amount'] = expenses_df['Amount'] * -1
            
            if not expenses_df.empty and 'Date' in expenses_df.columns:
                # Monthly trend
                monthly_data = expenses_df.groupby([
                    expenses_df['Date'].dt.to_period('M'),
                    'Category'
                ])['Amount'].sum().reset_index()
                monthly_data['Date'] = monthly_data['Date'].astype(str)
                
                fig_trend = create_trend_chart(monthly_data, 'Date', 'Amount', 'Category', 'Monthly Spending Trends')
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # Monthly comparison
                if len(monthly_data['Date'].unique()) >= 2:
                    comparison_data = expenses_df.groupby([
                        expenses_df['Date'].dt.to_period('M')
                    ])['Amount'].sum().reset_index()
                    comparison_data['Date'] = comparison_data['Date'].astype(str)
                    
                    fig_comparison = create_monthly_comparison(comparison_data, 'Date', 'Amount', 'Month-over-Month Comparison')
                    st.plotly_chart(fig_comparison, use_container_width=True)
            else:
                st.info("No date information available for trend analysis")
        
        with tab3:
            st.subheader("Financial Insights")
            
            expenses_df = df[df['Amount'] < 0].copy()
            expenses_df['Amount'] = expenses_df['Amount'] * -1
            
            if not expenses_df.empty:
                # Top spending insights
                category_totals = expenses_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
                total_expenses = category_totals.sum()
                
                st.write("**🎯 Key Insights:**")
                
                # Top category
                top_category = category_totals.index[0]
                top_amount = category_totals.iloc[0]
                top_percentage = (top_amount / total_expenses * 100)
                st.write(f"• Your biggest spending category is **{top_category}** at KSh {top_amount:,.2f} ({top_percentage:.1f}% of total expenses)")
                
                # Category breakdown
                for i, (category, amount) in enumerate(category_totals.head(5).items()):
                    percentage = (amount / total_expenses * 100)
                    st.write(f"• **{category}**: KSh {amount:,.2f} ({percentage:.1f}%)")
                
                # Monthly comparison if available
                if 'Date' in expenses_df.columns:
                    monthly_totals = expenses_df.groupby(expenses_df['Date'].dt.to_period('M'))['Amount'].sum()
                    if len(monthly_totals) >= 2:
                        latest_month = monthly_totals.iloc[-1]
                        previous_month = monthly_totals.iloc[-2]
                        change = ((latest_month - previous_month) / previous_month * 100)
                        
                        direction = "increased" if change > 0 else "decreased"
                        st.write(f"• Your spending has **{direction}** by {abs(change):.1f}% compared to the previous month")
                
                # High-value transactions
                high_value_threshold = expenses_df['Amount'].quantile(0.9)
                high_value_transactions = expenses_df[expenses_df['Amount'] >= high_value_threshold]
                
                if not high_value_transactions.empty:
                    st.write(f"**💸 High-Value Transactions (top 10%):**")
                    st.dataframe(
                        high_value_transactions[['Date', 'Details', 'Amount', 'Category']].head(10),
                        use_container_width=True
                    )
        
        with tab4:
            st.subheader("Category Management")
            
            # Show unknown/uncategorized transactions
            uncategorized = df[df['Category'] == 'Other']
            
            if not uncategorized.empty:
                st.write("**🔍 Uncategorized Transactions**")
                st.write("Assign categories to improve your analysis:")
                
                # Group by unique details for easier categorization
                unique_details = uncategorized.groupby('Details').agg({
                    'Amount': 'count'
                }).rename(columns={'Amount': 'Count'}).reset_index()
                
                for _, row in unique_details.head(20).iterrows():
                    detail = row['Details']
                    count = row['Count']
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{detail}** ({count} transactions)")
                    
                    with col2:
                        new_category = st.selectbox(
                            f"Category for {detail[:30]}...",
                            options=['Food', 'Transport', 'Utilities', 'Entertainment', 'Shopping', 'Health', 'Education', 'Other'],
                            key=f"cat_{detail}",
                            label_visibility="collapsed"
                        )
                        
                        if st.button(f"Assign", key=f"assign_{detail}"):
                            # Update category mapping
                            st.session_state.category_mappings[detail] = new_category
                            save_category_mappings(st.session_state.category_mappings)
                            
                            # Re-categorize data
                            categorizer = ExpenseCategorizer(st.session_state.category_mappings)
                            st.session_state.categorized_data = categorizer.categorize_transactions(st.session_state.processed_data)
                            
                            st.success(f"Assigned '{detail}' to {new_category}")
                            st.rerun()
            else:
                st.success("✅ All transactions are categorized!")
            
            # Show current mappings
            if st.session_state.category_mappings:
                st.write("**📝 Current Category Mappings**")
                mappings_df = pd.DataFrame([
                    {"Transaction Detail": k, "Category": v} 
                    for k, v in st.session_state.category_mappings.items()
                ])
                st.dataframe(mappings_df, use_container_width=True)
        
        with tab5:
            st.subheader("Export Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**📊 Export Categorized Transactions**")
                if st.button("Download CSV"):
                    csv_data = export_to_csv(df)
                    st.download_button(
                        label="Download Categorized Data",
                        data=csv_data,
                        file_name=f"mpesa_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                st.write("**📄 Export Summary Report**")
                if st.button("Generate Summary"):
                    # Create summary data
                    expenses_df = df[df['Amount'] < 0].copy()
                    expenses_df['Amount'] = expenses_df['Amount'] * -1
                    
                    summary_data = {
                        'total_transactions': len(df),
                        'total_spent': expenses_df['Amount'].sum(),
                        'category_breakdown': expenses_df.groupby('Category')['Amount'].sum().to_dict(),
                        'date_range': f"{df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}"
                    }
                    
                    summary_text = f"""
M-PESA STATEMENT ANALYSIS SUMMARY
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW:
- Analysis Period: {summary_data['date_range']}
- Total Transactions: {summary_data['total_transactions']}
- Total Amount Spent: KSh {summary_data['total_spent']:,.2f}

CATEGORY BREAKDOWN:
"""
                    for category, amount in sorted(summary_data['category_breakdown'].items(), key=lambda x: x[1], reverse=True):
                        percentage = (amount / summary_data['total_spent'] * 100)
                        summary_text += f"- {category}: KSh {amount:,.2f} ({percentage:.1f}%)\n"
                    
                    st.download_button(
                        label="Download Summary Report",
                        data=summary_text,
                        file_name=f"mpesa_summary_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
    
    else:
        # Welcome screen
        st.markdown("""
        ## 🚀 Get Started
        
        Upload your M-Pesa statement (CSV or PDF format) using the sidebar to begin analyzing your spending patterns.
        
        ### 📋 What you'll get:
        - **Expense categorization** into Food, Transport, Utilities, and more
        - **Interactive charts** showing your spending breakdown
        - **Trend analysis** to track spending patterns over time
        - **Smart insights** highlighting key spending behaviors
        - **Export functionality** for further analysis
        
        ### 📁 Supported Formats:
        - **CSV files** from Safaricom M-Pesa statements
        - **PDF files** from M-Pesa statement downloads
        
        ### 🔒 Privacy Note:
        Your data is processed locally and never stored on external servers.
        """)

if __name__ == "__main__":
    main()
