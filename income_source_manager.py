import streamlit as st
import pandas as pd
import json
from typing import Dict, List
from categorizer import ExpenseCategorizer

class IncomeSourceManager:
    def __init__(self):
        self.income_types = [
            'Salary',
            'Business Income', 
            'Freelance/Consulting',
            'Investment Returns',
            'Rental Income',
            'Side Hustle',
            'Regular Transfers',
            'Other Income'
        ]
    
    def render_income_source_setup(self, categorizer: ExpenseCategorizer, df: pd.DataFrame = None):
        """Render the income source setup interface"""
        st.subheader("💰 Income Source Configuration")
        st.write("Help the system better identify your income by specifying who pays you and what type of income it is.")
        
        # Show current configuration
        current_sources = categorizer.get_income_sources_config()
        
        if current_sources:
            st.write("**Current Income Sources:**")
            for income_type, payers in current_sources.items():
                with st.expander(f"{income_type} ({len(payers)} payers)"):
                    for payer in payers:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"• {payer}")
                        with col2:
                            if st.button("Remove", key=f"remove_{income_type}_{payer}"):
                                categorizer.remove_income_source(income_type, payer)
                                st.rerun()
        
        # Add new income source
        st.write("**Add New Income Source:**")
        
        col1, col2 = st.columns([2, 2])
        
        with col1:
            income_type = st.selectbox(
                "Income Type",
                self.income_types,
                key="new_income_type"
            )
        
        with col2:
            payer_name = st.text_input(
                "Payer Name/Description",
                placeholder="e.g., ABC Company, John Doe, Freelance Client",
                key="new_payer_name"
            )
        
        if st.button("Add Income Source"):
            if payer_name.strip():
                categorizer.add_income_source(income_type, [payer_name.strip()])
                st.success(f"Added {payer_name} as {income_type}")
                st.rerun()
            else:
                st.error("Please enter a payer name")
        
        # Smart suggestions based on data
        if df is not None and not df.empty:
            self._render_smart_suggestions(categorizer, df)
    
    def _render_smart_suggestions(self, categorizer: ExpenseCategorizer, df: pd.DataFrame):
        """Render smart suggestions based on transaction data"""
        st.write("**💡 Smart Suggestions**")
        st.write("Based on your transaction history, these might be income sources:")
        
        suggestions = categorizer.suggest_income_sources_from_data(df)
        
        if not suggestions:
            st.info("No recurring income patterns detected. Add your income sources manually above.")
            return
        
        for income_type, transactions in suggestions.items():
            with st.expander(f"Suggested {income_type} ({len(transactions)} transactions)"):
                for transaction in transactions:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"• {transaction}")
                    
                    with col2:
                        if st.button("Add", key=f"add_suggestion_{income_type}_{transaction}"):
                            categorizer.add_income_source(income_type, [transaction])
                            st.success(f"Added {transaction} as {income_type}")
                            st.rerun()
                    
                    with col3:
                        if st.button("Ignore", key=f"ignore_suggestion_{income_type}_{transaction}"):
                            # Add to custom mappings as 'Other' to prevent future suggestions
                            categorizer.add_custom_mapping(transaction, 'Other')
                            st.info("Transaction ignored")
                            st.rerun()
    
    def render_income_analysis_with_sources(self, df: pd.DataFrame, categorizer: ExpenseCategorizer):
        """Render enhanced income analysis with source breakdown"""
        if df.empty:
            st.warning("No transaction data available")
            return
        
        # Categorize transactions with user-defined sources
        categorized_df = categorizer.categorize_transactions(df)
        
        # Get income transactions
        income_df = categorized_df[
            categorized_df['Category'].str.contains('Income', na=False)
        ].copy()
        
        if income_df.empty:
            st.warning("No income transactions found. Please configure your income sources above.")
            return
        
        # Ensure positive amounts
        income_df['Amount'] = income_df['Amount'].abs()
        
        # Overall income metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_income = income_df['Amount'].sum()
            st.metric("Total Income", f"KSh {total_income:,.0f}")
        
        with col2:
            monthly_avg = income_df.groupby(
                pd.Grouper(key='Date', freq='ME')
            )['Amount'].sum().mean()
            st.metric("Monthly Average", f"KSh {monthly_avg:,.0f}")
        
        with col3:
            num_sources = len(income_df['Category'].unique())
            st.metric("Income Sources", num_sources)
        
        with col4:
            last_income = income_df['Date'].max()
            days_since = (pd.Timestamp.now() - last_income).days
            st.metric("Days Since Last Income", days_since)
        
        # Income breakdown by source
        st.subheader("Income Breakdown by Source")
        
        source_summary = income_df.groupby('Category').agg({
            'Amount': ['sum', 'count', 'mean'],
            'Date': ['min', 'max']
        }).round(2)
        
        source_summary.columns = ['Total', 'Count', 'Average', 'First_Date', 'Last_Date']
        source_summary = source_summary.sort_values('Total', ascending=False)
        
        # Add percentage
        source_summary['Percentage'] = (source_summary['Total'] / total_income * 100).round(1)
        
        # Display as chart and table
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Pie chart
            fig_data = source_summary['Total'].to_dict()
            if fig_data:
                st.write("**Income Distribution**")
                # Create a simple bar chart since pie charts need plotly
                chart_df = pd.DataFrame({
                    'Source': list(fig_data.keys()),
                    'Amount': list(fig_data.values())
                })
                st.bar_chart(chart_df.set_index('Source'))
        
        with col2:
            st.write("**Income Summary Table**")
            display_df = source_summary[['Total', 'Count', 'Percentage']].copy()
            display_df['Total'] = display_df['Total'].apply(lambda x: f"KSh {x:,.0f}")
            display_df['Percentage'] = display_df['Percentage'].apply(lambda x: f"{x}%")
            st.dataframe(display_df)
        
        # Recent income transactions
        st.subheader("Recent Income Transactions")
        recent_income = income_df.nlargest(10, 'Date')[['Date', 'Details', 'Amount', 'Category']]
        recent_income['Amount'] = recent_income['Amount'].apply(lambda x: f"KSh {x:,.0f}")
        st.dataframe(recent_income, use_container_width=True)
        
        # Income insights
        self._render_income_insights(income_df, source_summary)
    
    def _render_income_insights(self, income_df: pd.DataFrame, source_summary: pd.DataFrame):
        """Render income insights and recommendations"""
        st.subheader("💡 Income Insights")
        
        insights = []
        
        # Diversification insight
        num_sources = len(source_summary)
        if num_sources == 1:
            insights.append("⚠️ **Single Income Source Risk**: You rely on one income source. Consider diversifying to reduce financial risk.")
        elif num_sources >= 3:
            insights.append("✅ **Good Diversification**: You have multiple income sources, which provides financial stability.")
        
        # Regularity insight
        monthly_income = income_df.groupby(pd.Grouper(key='Date', freq='ME'))['Amount'].sum()
        if len(monthly_income) >= 2:
            cv = monthly_income.std() / monthly_income.mean()
            if cv < 0.2:
                insights.append("✅ **Stable Income**: Your income is consistent month-to-month.")
            else:
                insights.append("⚠️ **Variable Income**: Your income fluctuates significantly. Consider building a larger emergency fund.")
        
        # Growth insight
        if len(monthly_income) >= 3:
            recent_avg = monthly_income.tail(3).mean()
            earlier_avg = monthly_income.head(3).mean()
            growth = (recent_avg - earlier_avg) / earlier_avg * 100
            
            if growth > 10:
                insights.append(f"📈 **Growing Income**: Your income has grown by {growth:.1f}% - great progress!")
            elif growth < -10:
                insights.append(f"📉 **Declining Income**: Your income has decreased by {abs(growth):.1f}%. Consider exploring new opportunities.")
        
        # Top source dependency
        if not source_summary.empty:
            top_source_pct = source_summary.iloc[0]['Percentage']
            if top_source_pct > 80:
                insights.append(f"⚠️ **High Dependency**: {top_source_pct:.1f}% of your income comes from one source. This increases financial risk.")
        
        for insight in insights:
            st.write(insight)
        
        if not insights:
            st.info("Keep tracking your income to get personalized insights!")
    
    def save_income_config(self, categorizer: ExpenseCategorizer, filename: str = "income_config.json"):
        """Save income source configuration to file"""
        config = {
            'income_sources': categorizer.get_income_sources_config(),
            'custom_mappings': categorizer.custom_mappings
        }
        
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        
        return filename
    
    def load_income_config(self, filename: str = "income_config.json") -> Dict:
        """Load income source configuration from file"""
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            return {'income_sources': {}, 'custom_mappings': {}}