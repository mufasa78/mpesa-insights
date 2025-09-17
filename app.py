import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import io

from data_processor import DataProcessor
from categorizer import ExpenseCategorizer
from visualizer import create_pie_chart, create_bar_chart, create_monthly_comparison
from utils import export_to_csv, export_summary_to_pdf
from budget_advisor import BudgetAdvisor
from expense_predictor import ExpensePredictor
from spending_comparator import SpendingComparator
from income_tracker import IncomeTracker
from income_source_manager import IncomeSourceManager
from feedback_donation_system import FeedbackDonationSystem

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
if 'show_feedback' not in st.session_state:
    st.session_state.show_feedback = False

# Initialize feedback and donation system
feedback_system = FeedbackDonationSystem()

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

def render_dashboard_section(df):
    """Render the main dashboard section"""
    st.header("📊 Financial Dashboard")
    
    # Sub-tabs for dashboard
    dash_tab1, dash_tab2, dash_tab3 = st.tabs([
        "📈 Overview", "📊 Spending Analysis", "📉 Trends"
    ])
    
    with dash_tab1:
        st.subheader("💰 Financial Overview")
        
        # Key metrics
        total_transactions = len(df)
        income_df = df[df['Amount'] > 0]
        expense_df = df[df['Amount'] < 0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Transactions", f"{total_transactions:,}")
        
        with col2:
            total_income = income_df['Amount'].sum()
            st.metric("Total Income", f"KSh {total_income:,.0f}")
        
        with col3:
            total_expenses = expense_df['Amount'].sum()
            st.metric("Total Expenses", f"KSh {abs(total_expenses):,.0f}")
        
        with col4:
            net_flow = total_income + total_expenses
            st.metric("Net Cash Flow", f"KSh {net_flow:,.0f}", 
                     delta=f"{'Positive' if net_flow > 0 else 'Negative'}")
        
        # Quick expense breakdown
        expenses_df = df[df['Amount'] < 0].copy()
        
        if not expenses_df.empty:
            expenses_df['Amount'] = expenses_df['Amount'] * -1  # Make positive for display
            
            # Top 5 categories
            top_categories = expenses_df.groupby('Category')['Amount'].sum().nlargest(5)
            
            st.subheader("🏆 Top Spending Categories")
            for i, (category, amount) in enumerate(top_categories.items(), 1):
                percentage = (amount / expenses_df['Amount'].sum()) * 100
                st.write(f"{i}. **{category}**: KSh {amount:,.0f} ({percentage:.1f}%)")
        
        # Recent transactions
        st.subheader("📝 Recent Transactions")
        recent_transactions = df.nlargest(10, 'Date')[['Date', 'Details', 'Amount', 'Category']]
        recent_transactions['Amount'] = recent_transactions['Amount'].apply(lambda x: f"KSh {x:,.0f}")
        st.dataframe(recent_transactions, use_container_width=True)
    
    with dash_tab2:
        st.subheader("📊 Detailed Spending Analysis")
        
        # Filter for expenses only
        expenses_df = df[df['Amount'] < 0].copy()
        
        if not expenses_df.empty:
            expenses_df['Amount'] = expenses_df['Amount'] * -1
            
            # Category analysis
            category_summary = expenses_df.groupby('Category').agg({
                'Amount': ['sum', 'count', 'mean']
            }).round(2)
            
            category_summary.columns = ['Total', 'Count', 'Average']
            category_summary = category_summary.sort_values('Total', ascending=False)
            
            # Add percentage
            total_expenses = category_summary['Total'].sum()
            category_summary['Percentage'] = (category_summary['Total'] / total_expenses * 100).round(1)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart
                fig_pie = create_pie_chart(category_summary.reset_index(), 'Category', 'Total', 'Expense Breakdown')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Bar chart
                fig_bar = create_bar_chart(category_summary.reset_index(), 'Category', 'Total', 'Spending by Category')
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Category summary table
            st.subheader("📋 Detailed Category Breakdown")
            
            # Format for display
            display_summary = category_summary.copy()
            display_summary['Total'] = display_summary['Total'].apply(lambda x: f"KSh {x:,.2f}")
            display_summary['Average'] = display_summary['Average'].apply(lambda x: f"KSh {x:,.2f}")
            display_summary['Percentage'] = display_summary['Percentage'].apply(lambda x: f"{x}%")
            
            st.dataframe(display_summary, use_container_width=True)
        else:
            st.info("No expense transactions found in the selected data")
    
    with dash_tab3:
        st.subheader("📈 Spending Trends")
        
        if 'Date' in df.columns:
            # Monthly trends
            df['Month'] = df['Date'].dt.to_period('M')
            monthly_data = df.groupby('Month').agg({
                'Amount': 'sum'
            }).reset_index()
            
            monthly_data['Month'] = monthly_data['Month'].astype(str)
            monthly_data['Amount'] = monthly_data['Amount'].abs()
            
            if len(monthly_data) > 1:
                # Create a simple line chart for monthly trends
                import plotly.express as px
                fig_trend = px.line(
                    monthly_data, 
                    x='Month', 
                    y='Amount',
                    title='Monthly Spending Trend',
                    markers=True
                )
                fig_trend.update_traces(
                    hovertemplate='<b>Month: %{x}</b><br>Amount: KSh %{y:,.0f}<extra></extra>'
                )
                fig_trend.update_layout(
                    xaxis_title='Month',
                    yaxis_title='Amount (KSh)',
                    height=400
                )
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # Month-over-month comparison
                if len(monthly_data) >= 2:
                    comparison_data = monthly_data.copy()
                    comparison_data['Previous_Month'] = comparison_data['Amount'].shift(1)
                    comparison_data['Change'] = comparison_data['Amount'] - comparison_data['Previous_Month']
                    comparison_data['Change_Percent'] = (comparison_data['Change'] / comparison_data['Previous_Month'] * 100).round(1)
                    
                    st.subheader("📊 Month-over-Month Changes")
                    for _, row in comparison_data.dropna().iterrows():
                        change = row['Change']
                        change_pct = row['Change_Percent']
                        if change > 0:
                            st.write(f"📈 {row['Month']}: +KSh {change:,.0f} (+{change_pct}%)")
                        else:
                            st.write(f"📉 {row['Month']}: KSh {change:,.0f} ({change_pct}%)")
        else:
            st.info("No date information available for trend analysis")

def render_income_budget_section(df):
    """Render income and budget analysis section"""
    st.header("💰 Income & Budget Analysis")
    
    # Sub-tabs for income and budget
    income_tab1, income_tab2, income_tab3 = st.tabs([
        "💰 Income Tracker", "🎯 Budget Coach", "📊 Benchmarks"
    ])
    
    with income_tab1:
        st.subheader("💰 Income Analysis & Source Management")
        
        # Initialize income source manager
        income_source_manager = IncomeSourceManager()
        
        # Load income configuration if exists
        try:
            income_config = income_source_manager.load_income_config()
            enhanced_categorizer = ExpenseCategorizer(
                st.session_state.category_mappings,
                income_config.get('income_sources', {})
            )
        except:
            enhanced_categorizer = ExpenseCategorizer(st.session_state.category_mappings)
        
        # Create tabs within the Income Tracker
        income_subtab1, income_subtab2, income_subtab3 = st.tabs([
            "🔧 Setup Income Sources", "📊 Income Analysis", "💡 Insights & Tips"
        ])
        
        with income_subtab1:
            # Income source configuration
            income_source_manager.render_income_source_setup(enhanced_categorizer, df)
            
            # Save configuration
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("💾 Save Income Configuration"):
                    filename = income_source_manager.save_income_config(enhanced_categorizer)
                    st.success(f"Configuration saved to {filename}")
            
            with col2:
                if st.button("🔄 Re-categorize with New Sources"):
                    # Re-categorize all data with updated income sources
                    st.session_state.categorized_data = enhanced_categorizer.categorize_transactions(st.session_state.processed_data)
                    st.success("Data re-categorized with updated income sources!")
                    st.rerun()
        
        with income_subtab2:
            # Enhanced income analysis with source breakdown
            income_source_manager.render_income_analysis_with_sources(df, enhanced_categorizer)
            
            # Traditional income analysis for comparison
            st.subheader("📈 Income vs Expenses Comparison")
            income_tracker = IncomeTracker()
            savings_data = income_tracker.calculate_savings_rate(df)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Monthly Income", f"KSh {savings_data['monthly_income']:,.0f}")
            
            with col2:
                st.metric("Monthly Expenses", f"KSh {savings_data['monthly_expenses']:,.0f}")
            
            with col3:
                st.metric("Monthly Savings", f"KSh {savings_data['monthly_savings']:,.0f}")
            
            with col4:
                savings_rate = savings_data['savings_rate']
                if savings_rate >= 20:
                    st.metric("Savings Rate", f"{savings_rate:.1f}%", delta="Excellent")
                elif savings_rate >= 10:
                    st.metric("Savings Rate", f"{savings_rate:.1f}%", delta="Good")
                elif savings_rate >= 5:
                    st.metric("Savings Rate", f"{savings_rate:.1f}%", delta="Fair")
                else:
                    st.metric("Savings Rate", f"{savings_rate:.1f}%", delta="Poor")
        
        with income_subtab3:
            # Income improvement suggestions
            income_tracker = IncomeTracker()
            income_analysis = income_tracker.analyze_income_patterns(df)
            income_suggestions = income_tracker.suggest_income_improvements(income_analysis)
            
            if income_suggestions:
                st.subheader("📈 Income Improvement Suggestions")
                
                for suggestion in income_suggestions:
                    with st.expander(f"{suggestion['category']}: {suggestion['potential_impact']}"):
                        st.write(f"**Suggestion:** {suggestion['suggestion']}")
                        st.write(f"**Potential Impact:** {suggestion['potential_impact']}")
                        st.write(f"**Effort Level:** {suggestion['effort']}")
                        st.write(f"**Timeframe:** {suggestion['timeframe']}")
    
    with income_tab2:
        st.subheader("🎯 Budget Coach & Expense Optimization")
        
        # Initialize budget advisor and income tracker
        budget_advisor = BudgetAdvisor()
        income_tracker = IncomeTracker()
        
        # Calculate savings data
        savings_data = income_tracker.calculate_savings_rate(df)
        
        # Budget analysis using correct method
        budget_insights = budget_advisor.analyze_spending_patterns(df)
        
        # Display budget metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Calculate a simple budget score based on overspending
            overspending_cats = budget_insights.get('overspending_categories', [])
            budget_score = max(0, 100 - (len(overspending_cats) * 15))
            st.metric("Budget Score", f"{budget_score:.0f}/100")
        
        with col2:
            overspending_count = len(overspending_cats)
            st.metric("Overspending Categories", overspending_count)
        
        with col3:
            if savings_data['savings_rate'] < 20:
                needed_reduction = (20 - savings_data['savings_rate']) / 100 * savings_data['monthly_income']
                st.metric("To Reach 20% Savings", f"Reduce expenses by KSh {needed_reduction:,.2f}")
            else:
                st.metric("Savings Goal", "✅ Achieved!")
        
        with col4:
            # Calculate potential savings from overspending categories
            potential_savings = sum(cat.get('excess_amount', 0) for cat in overspending_cats)
            st.metric("Potential Monthly Savings", f"KSh {potential_savings:,.0f}")
        
        # Budget recommendations
        if overspending_cats:
            st.subheader("💡 Budget Optimization Tips")
            
            for cat in overspending_cats:
                category = cat['category']
                excess = cat['excess_amount']
                current_pct = cat['current_percentage']
                recommended_pct = cat['recommended_percentage']
                
                priority_color = "🔴" if excess > 5000 else "🟡" if excess > 2000 else "🟢"
                with st.expander(f"{priority_color} Reduce {category} Spending"):
                    st.write(f"**Current Spending:** {current_pct:.1f}% of expenses")
                    st.write(f"**Recommended:** {recommended_pct:.1f}% of expenses")
                    st.write(f"**Excess Amount:** KSh {excess:,.0f}")
                    st.write(f"**Action:** Consider reducing {category.lower()} expenses to stay within recommended budget")
        
        # Savings opportunities
        savings_opportunities = budget_insights.get('savings_opportunities', [])
        if savings_opportunities:
            st.subheader("💰 Savings Opportunities")
            
            for opportunity in savings_opportunities:
                opportunity_type = opportunity.get('type', 'General')
                suggestion = opportunity.get('suggestion', 'No suggestion available')
                potential_savings = opportunity.get('potential_savings', 0)
                description = opportunity.get('description', 'No description available')
                
                with st.expander(f"💰 {opportunity_type.replace('_', ' ').title()} - Save up to KSh {potential_savings:,.0f}"):
                    st.write(f"**Description:** {description}")
                    st.write(f"**Suggestion:** {suggestion}")
                    st.write(f"**Potential Savings:** KSh {potential_savings:,.0f}")
        
        # Expense cutting tips
        tips = budget_advisor.generate_expense_cutting_tips(budget_insights)
        if tips:
            st.subheader("✂️ Expense Cutting Tips")
            for tip in tips:
                st.write(f"💡 {tip}")
    
    with income_tab3:
        st.subheader("📊 Spending Benchmarks & Comparisons")
        
        # Initialize comparator and income tracker
        comparator = SpendingComparator()
        income_tracker = IncomeTracker()
        
        # Get income for benchmarking
        savings_data = income_tracker.calculate_savings_rate(df)
        monthly_income = savings_data['monthly_income']
        
        if monthly_income > 0:
            # Get spending comparison using correct method
            comparison_data = comparator.compare_with_benchmarks(df, monthly_income)
            
            st.subheader("📈 How You Compare to Benchmarks")
            
            # Display overall spending score
            overall_score_data = comparison_data.get('overall_score', {})
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if isinstance(overall_score_data, dict):
                    overall_score = overall_score_data.get('overall_score', 0)
                else:
                    overall_score = 0
                st.metric("Overall Spending Score", f"{overall_score:.0f}/100")
            
            with col2:
                income_bracket = comparison_data.get('income_bracket', 'Unknown')
                st.metric("Income Bracket", income_bracket.title())
            
            with col3:
                if isinstance(overall_score_data, dict):
                    efficient_categories = overall_score_data.get('efficient_categories', 0)
                else:
                    efficient_categories = len([c for c in category_comparisons.values() if c.get('status') == 'optimal'])
                st.metric("Efficient Categories", efficient_categories)
            
            # Category comparison
            category_comparisons = comparison_data.get('comparisons', {})
            if category_comparisons:
                st.subheader("📊 Category Breakdown")
                
                comparison_df = []
                for category, data in category_comparisons.items():
                    user_amount = data.get('your_spending', 0)
                    benchmark_range = data.get('benchmark_range', 'N/A')
                    status = data.get('status', 'unknown')
                    percentage = data.get('percentage_of_optimal', 100)
                    
                    status_emoji = '🟢' if status == 'optimal' else '🟡' if status == 'acceptable' else '🔴'
                    
                    comparison_df.append({
                        'Category': category,
                        'Your Spending': f"KSh {user_amount:,.0f}",
                        'Benchmark Range': f"KSh {benchmark_range}",
                        'vs Optimal': f"{percentage:.0f}%",
                        'Status': f"{status_emoji} {status.title()}"
                    })
                
                if comparison_df:
                    comparison_df = pd.DataFrame(comparison_df)
                    st.dataframe(comparison_df, use_container_width=True)
            
            # Spending efficiency analysis
            efficiency_data = comparator.analyze_spending_efficiency(df)
            
            st.subheader("⚡ Spending Efficiency Insights")
            
            efficiency_score = efficiency_data.get('efficiency_score', 0)
            if efficiency_score > 75:
                st.success(f"✅ **Excellent spending efficiency**: {efficiency_score:.1f}%")
            elif efficiency_score > 60:
                st.info(f"ℹ️ **Good spending efficiency**: {efficiency_score:.1f}%")
            else:
                st.warning(f"⚠️ **Room for improvement**: {efficiency_score:.1f}% efficiency")
            
            # Efficiency insights
            insights = efficiency_data.get('insights', [])
            if insights:
                st.write("**Key Insights:**")
                for insight in insights:
                    st.write(f"• {insight}")
            
            # Cost-saving alternatives
            alternatives = comparator.find_cost_saving_alternatives(df)
            if alternatives:
                st.subheader("💡 Cost-Saving Suggestions")
                
                for alt in alternatives[:5]:  # Show top 5
                    with st.expander(f"💰 {alt['category']}: Save up to KSh {alt['potential_savings']:,.0f}"):
                        st.write(f"**Current Pattern:** {alt['current_pattern']}")
                        st.write(f"**Suggestion:** {alt['suggestion']}")
                        st.write(f"**Potential Monthly Savings:** KSh {alt['potential_savings']:,.0f}")
        
        else:
            st.warning("⚠️ Income information needed for benchmark comparison. Please set up your income sources in the Income Tracker tab.")

def render_ai_insights_section(df):
    """Render AI insights section"""
    st.header("🧠 AI-Powered Insights")
    
    # Sub-tabs for AI insights
    ai_tab1, ai_tab2 = st.tabs([
        "🔮 Predictions & Forecasting", "🧠 Behavior Analysis"
    ])
    
    with ai_tab1:
        st.subheader("🔮 Expense Predictions & Goal Setting")
        
        # Initialize predictor and income tracker
        predictor = ExpensePredictor()
        income_tracker = IncomeTracker()
        
        # Get predictions
        predictions = predictor.predict_expenses(df)
        
        # Display predictions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            next_month = predictions.get('next_month_total', 0)
            st.metric("Next Month Prediction", f"KSh {next_month:,.0f}")
        
        with col2:
            trend = predictions.get('trend', 'stable')
            trend_emoji = "📈" if trend == "increasing" else "📉" if trend == "decreasing" else "➡️"
            st.metric("Spending Trend", f"{trend_emoji} {trend.title()}")
        
        with col3:
            confidence = predictions.get('confidence', 0)
            st.metric("Prediction Confidence", f"{confidence:.0f}%")
        
        # Category predictions
        category_predictions = predictions.get('category_predictions', {})
        if category_predictions:
            st.subheader("📊 Category Predictions")
            
            pred_df = pd.DataFrame([
                {
                    'Category': category,
                    'Predicted Amount': f"KSh {data['predicted_amount']:,.0f}",
                    'Confidence': f"{data['confidence']*100:.0f}%",
                    'Trend': data['trend']
                }
                for category, data in category_predictions.items()
            ])
            
            st.dataframe(pred_df, use_container_width=True)
        
        # Goal setting
        st.subheader("🎯 Financial Goal Setting")
        
        savings_data = income_tracker.calculate_savings_rate(df)
        current_savings_rate = savings_data['savings_rate']
        
        target_savings_rate = st.slider(
            "Target Savings Rate (%)",
            min_value=5,
            max_value=50,
            value=max(20, int(current_savings_rate) + 5),
            step=5
        )
        
        if target_savings_rate > current_savings_rate:
            needed_reduction = (target_savings_rate - current_savings_rate) / 100 * savings_data['monthly_income']
            st.info(f"💡 To reach {target_savings_rate}% savings rate, reduce monthly expenses by KSh {needed_reduction:,.0f}")
            
            # Suggest which categories to reduce based on current spending
            expenses_df = df[df['Amount'] < 0].copy()
            if not expenses_df.empty:
                expenses_df['Amount'] = expenses_df['Amount'].abs()
                category_spending = expenses_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
                
                st.write("**Suggested reductions by category:**")
                
                # Calculate needed reduction per category (proportional to spending)
                total_reduction_needed = needed_reduction
                total_current_spending = category_spending.sum()
                
                for category, amount in category_spending.head(5).items():
                    if category != 'Income':  # Don't suggest reducing income
                        category_proportion = amount / total_current_spending
                        suggested_reduction = total_reduction_needed * category_proportion
                        reduction_percentage = (suggested_reduction / amount) * 100
                        
                        st.write(f"• **{category}**: Reduce by KSh {suggested_reduction:,.0f} ({reduction_percentage:.1f}%)")
            else:
                st.info("💡 Focus on increasing income or tracking more expense transactions for specific recommendations")
    
    with ai_tab2:
        st.subheader("🧠 Advanced Markov Chain Behavior Analysis")
        
        try:
            # Import and initialize Markov Chain components
            from markov_predictor import MarkovChainPredictor
            from behavior_analyzer import BehaviorAnalyzer
            
            # Create sub-tabs for different Markov Chain analyses
            markov_tab1, markov_tab2, markov_tab3, markov_tab4 = st.tabs([
                "🔮 Predictive Modeling", "⚠️ Anomaly Detection", "📊 Behavioral Patterns", "💡 AI Insights"
            ])
            
            with markov_tab1:
                st.subheader("🔮 Markov Chain Predictive Modeling")
                
                if len(df) < 10:
                    st.warning("⚠️ Need at least 10 transactions for reliable Markov Chain analysis")
                else:
                    with st.spinner("🧠 Training Markov Chain model..."):
                        # Initialize and train Markov model
                        markov_model = MarkovChainPredictor(order=2)
                        markov_model.train(df)
                        
                        # Model statistics
                        stats = markov_model.get_model_stats()
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Model Status", stats.get('status', 'Unknown'))
                        with col2:
                            st.metric("Behavioral States", stats.get('total_states', 0))
                        with col3:
                            st.metric("Learned Transitions", stats.get('total_transitions', 0))
                        with col4:
                            st.metric("Pattern Complexity", f"Order {stats.get('order', 1)}")
                        
                        # Next transaction predictions
                        st.subheader("🎯 Next Transaction Predictions")
                        
                        # Get recent state for prediction
                        df_with_states = markov_model.create_states(df)
                        if not df_with_states.empty:
                            recent_state = df_with_states.iloc[-1]['State_Sequence']
                            
                            st.write(f"**Current State:** `{recent_state}`")
                            
                            predictions = markov_model.predict_next_transaction(recent_state, n_predictions=5)
                            
                            if predictions and predictions[0]['state'] != 'Unknown':
                                st.write("**Most Likely Next Transactions:**")
                                
                                for i, pred in enumerate(predictions, 1):
                                    confidence_color = "🟢" if pred['confidence'] == 'High' else "🟡" if pred['confidence'] == 'Medium' else "🔴"
                                    
                                    with st.expander(f"{i}. {pred['category']} - {pred['probability']:.1%} probability"):
                                        st.write(f"**Confidence:** {confidence_color} {pred['confidence']}")
                                        st.write(f"**Amount Range:** {pred['amount_range']}")
                                        st.write(f"**Time Period:** {pred['time_period']}")
                                        st.write(f"**Probability:** {pred['probability']:.1%}")
                            else:
                                st.info("🔄 Need more transaction history for accurate predictions")
                        
                        # Spending sequence predictions
                        st.subheader("🔄 Spending Sequence Forecasting")
                        
                        categories = df['Category'].unique()[:3]  # Top 3 categories
                        
                        for category in categories:
                            if category != 'Other':
                                sequences = markov_model.predict_spending_sequence(category, sequence_length=4)
                                
                                if sequences and sequences[0]['sequence']:
                                    sequence_data = sequences[0]
                                    sequence = sequence_data['sequence']
                                    probability = sequence_data['overall_probability']
                                    
                                    st.write(f"**Starting with {category}:**")
                                    sequence_str = " → ".join(sequence)
                                    st.write(f"Likely sequence: `{sequence_str}`")
                                    st.write(f"Probability: {probability:.1%}")
                                    st.write("---")
                        
                        # Monthly forecasting
                        st.subheader("📅 Monthly Spending Forecast")
                        
                        monthly_forecast = markov_model.predict_monthly_spending()
                        
                        if monthly_forecast:
                            forecast_data = []
                            for category, data in monthly_forecast.items():
                                if category != 'Other':
                                    forecast_data.append({
                                        'Category': category,
                                        'Predicted Amount': data['predicted_amount'],
                                        'Lower Bound': data['confidence_interval'][0],
                                        'Upper Bound': data['confidence_interval'][1],
                                        'Expected Transactions': data['transaction_count']
                                    })
                            
                            if forecast_data:
                                forecast_df = pd.DataFrame(forecast_data)
                                
                                # Create forecast visualization
                                import plotly.graph_objects as go
                                
                                fig = go.Figure()
                                
                                fig.add_trace(go.Bar(
                                    name='Predicted Amount',
                                    x=forecast_df['Category'],
                                    y=forecast_df['Predicted Amount'],
                                    error_y=dict(
                                        type='data',
                                        symmetric=False,
                                        array=forecast_df['Upper Bound'] - forecast_df['Predicted Amount'],
                                        arrayminus=forecast_df['Predicted Amount'] - forecast_df['Lower Bound']
                                    )
                                ))
                                
                                fig.update_layout(
                                    title="Monthly Spending Forecast by Category",
                                    xaxis_title="Category",
                                    yaxis_title="Amount (KSh)",
                                    showlegend=False,
                                    height=400
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Forecast table
                                display_df = forecast_df.copy()
                                for col in ['Predicted Amount', 'Lower Bound', 'Upper Bound']:
                                    display_df[col] = display_df[col].apply(lambda x: f"KSh {x:,.0f}")
                                
                                st.dataframe(display_df, use_container_width=True)
            
            with markov_tab2:
                st.subheader("⚠️ AI-Powered Anomaly Detection")
                
                if len(df) < 10:
                    st.warning("⚠️ Need at least 10 transactions for anomaly detection")
                else:
                    with st.spinner("🔍 Detecting anomalies..."):
                        # Initialize and train model for anomaly detection
                        markov_model = MarkovChainPredictor(order=2)
                        markov_model.train(df)
                        
                        # Detect anomalies
                        anomalies = markov_model.detect_anomalies(df, threshold=0.1)
                        
                        # Anomaly summary
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Anomalies", len(anomalies))
                        
                        with col2:
                            anomaly_rate = len(anomalies) / len(df) * 100 if len(df) > 0 else 0
                            st.metric("Anomaly Rate", f"{anomaly_rate:.1f}%")
                        
                        with col3:
                            high_risk = len(anomalies[anomalies['anomaly_score'] > 0.8]) if not anomalies.empty else 0
                            st.metric("High Risk", high_risk)
                        
                        with col4:
                            categories_affected = len(anomalies['category'].unique()) if not anomalies.empty else 0
                            st.metric("Categories Affected", categories_affected)
                        
                        if not anomalies.empty:
                            # Anomaly distribution by category
                            st.subheader("📊 Anomaly Distribution")
                            
                            anomaly_categories = anomalies['category'].value_counts()
                            
                            if not anomaly_categories.empty:
                                import plotly.express as px
                                
                                fig = px.pie(
                                    values=anomaly_categories.values,
                                    names=anomaly_categories.index,
                                    title="Anomalies by Category"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            
                            # High-risk anomalies
                            high_risk_anomalies = anomalies[anomalies['anomaly_score'] > 0.8]
                            
                            if not high_risk_anomalies.empty:
                                st.subheader("🚨 High-Risk Anomalies")
                                
                                for _, anomaly in high_risk_anomalies.head(5).iterrows():
                                    with st.expander(f"🔴 {anomaly['date']} - {anomaly['category']} - KSh {anomaly['amount']:,.0f}"):
                                        st.write(f"**Transaction:** {anomaly['details']}")
                                        st.write(f"**Anomaly Score:** {anomaly['anomaly_score']:.1%}")
                                        st.write(f"**Reason:** {anomaly['reason']}")
                                        
                                        if anomaly['anomaly_score'] > 0.9:
                                            st.error("🔴 **Very High Risk** - This transaction is extremely unusual")
                                        else:
                                            st.warning("🟡 **High Risk** - This transaction deviates significantly from your patterns")
                            
                            # All anomalies table
                            st.subheader("📋 All Detected Anomalies")
                            
                            display_anomalies = anomalies.copy()
                            display_anomalies['date'] = pd.to_datetime(display_anomalies['date']).dt.strftime('%Y-%m-%d')
                            display_anomalies['amount'] = display_anomalies['amount'].apply(lambda x: f"KSh {x:,.0f}")
                            display_anomalies['anomaly_score'] = display_anomalies['anomaly_score'].apply(lambda x: f"{x:.1%}")
                            
                            st.dataframe(display_anomalies[['date', 'category', 'amount', 'anomaly_score', 'reason']], use_container_width=True)
                        
                        else:
                            st.success("✅ No significant anomalies detected in your spending patterns!")
            
            with markov_tab3:
                st.subheader("📊 Deep Behavioral Pattern Analysis")
                
                if len(df) < 10:
                    st.warning("⚠️ Need at least 10 transactions for pattern analysis")
                else:
                    with st.spinner("🧠 Analyzing behavioral patterns..."):
                        # Initialize behavior analyzer
                        behavior_analyzer = BehaviorAnalyzer()
                        analysis = behavior_analyzer.analyze_behavior(df)
                        
                        # Behavioral metrics
                        dashboard = behavior_analyzer.create_behavior_dashboard(analysis)
                        summary_metrics = dashboard.get('summary_metrics', {})
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            behavior_score = summary_metrics.get('behavior_score', 0)
                            st.metric("Behavior Score", f"{behavior_score:.0f}/100")
                        
                        with col2:
                            predictability = summary_metrics.get('predictability', 0)
                            st.metric("Predictability", f"{predictability:.0f}%")
                        
                        with col3:
                            anomaly_rate = summary_metrics.get('anomaly_rate', 0)
                            st.metric("Anomaly Rate", f"{anomaly_rate:.1f}%")
                        
                        with col4:
                            risk_level = summary_metrics.get('risk_level', 'Unknown')
                            color = 'red' if risk_level == 'High' else 'orange' if risk_level == 'Medium' else 'green'
                            st.markdown(f"**Risk Level:** :{color}[{risk_level}]")
                        
                        # Behavioral patterns
                        patterns = analysis.get('behavioral_patterns', {})
                        
                        # Most common transitions
                        st.subheader("🔄 Most Common Spending Transitions")
                        
                        transitions = patterns.get('most_common_transitions', [])
                        if transitions:
                            transition_data = []
                            for trans in transitions[:10]:
                                from_parts = trans['from_state'].split('_')
                                to_parts = trans['to_state'].split('_')
                                
                                transition_data.append({
                                    'From Category': from_parts[0] if from_parts else 'Unknown',
                                    'To Category': to_parts[0] if to_parts else 'Unknown',
                                    'Probability': f"{trans['probability']:.1%}",
                                    'Frequency': f"{trans['frequency']:.0f}"
                                })
                            
                            transition_df = pd.DataFrame(transition_data)
                            st.dataframe(transition_df, use_container_width=True)
                        
                        # Spending habits analysis
                        st.subheader("🎯 Spending Habits Analysis")
                        
                        habits = patterns.get('spending_habits', {})
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Daily Preferences:**")
                            daily_prefs = habits.get('daily_preferences', {})
                            for day, categories in daily_prefs.items():
                                if categories:
                                    top_category = categories[0][0] if categories[0] else 'None'
                                    count = categories[0][1] if categories[0] else 0
                                    st.write(f"• {day}: {top_category} ({count} times)")
                        
                        with col2:
                            st.write("**Time-based Preferences:**")
                            time_prefs = habits.get('time_preferences', {})
                            for period, categories in time_prefs.items():
                                if categories:
                                    top_category = categories[0][0] if categories[0] else 'None'
                                    count = categories[0][1] if categories[0] else 0
                                    st.write(f"• {period}: {top_category} ({count} times)")
            
            with markov_tab4:
                st.subheader("💡 AI-Generated Insights & Recommendations")
                
                if len(df) < 10:
                    st.warning("⚠️ Need at least 10 transactions for AI insights")
                else:
                    with st.spinner("🤖 Generating AI insights..."):
                        # Initialize behavior analyzer
                        behavior_analyzer = BehaviorAnalyzer()
                        analysis = behavior_analyzer.analyze_behavior(df)
                        
                        # Behavioral insights
                        patterns = analysis.get('behavioral_patterns', {})
                        insights = patterns.get('behavioral_insights', [])
                        
                        if insights:
                            st.subheader("🧠 Key Behavioral Insights")
                            for insight in insights:
                                st.info(f"💡 {insight}")
                        
                        # Risk assessment
                        risks = analysis.get('risk_assessment', {})
                        if risks:
                            st.subheader("⚠️ Risk Assessment")
                            
                            for risk_type, risk_data in risks.items():
                                if isinstance(risk_data, dict):
                                    risk_score = risk_data.get('risk_score', 0)
                                    description = risk_data.get('description', 'Unknown')
                                    
                                    col1, col2, col3 = st.columns([2, 1, 2])
                                    
                                    with col1:
                                        st.write(f"**{risk_type.replace('_', ' ').title()}**")
                                    
                                    with col2:
                                        color = 'red' if description == 'High' else 'orange' if description == 'Medium' else 'green'
                                        st.markdown(f":{color}[{description}]")
                                    
                                    with col3:
                                        st.progress(risk_score)
                        
                        # Recommendations
                        recommendations = analysis.get('recommendations', [])
                        if recommendations:
                            st.subheader("🎯 AI-Powered Recommendations")
                            
                            # Group by priority
                            high_priority = [r for r in recommendations if r.get('priority') == 'High']
                            medium_priority = [r for r in recommendations if r.get('priority') == 'Medium']
                            low_priority = [r for r in recommendations if r.get('priority') == 'Low']
                            
                            if high_priority:
                                st.write("**🔴 High Priority:**")
                                for rec in high_priority:
                                    with st.expander(f"🚨 {rec['title']}"):
                                        st.write(f"**Issue:** {rec['description']}")
                                        st.write(f"**Action:** {rec['action']}")
                                        st.write(f"**Expected Impact:** {rec['impact']}")
                            
                            if medium_priority:
                                st.write("**🟡 Medium Priority:**")
                                for rec in medium_priority:
                                    with st.expander(f"⚠️ {rec['title']}"):
                                        st.write(f"**Issue:** {rec['description']}")
                                        st.write(f"**Action:** {rec['action']}")
                                        st.write(f"**Expected Impact:** {rec['impact']}")
                            
                            if low_priority:
                                st.write("**🟢 Low Priority:**")
                                for rec in low_priority:
                                    with st.expander(f"💡 {rec['title']}"):
                                        st.write(f"**Issue:** {rec['description']}")
                                        st.write(f"**Action:** {rec['action']}")
                                        st.write(f"**Expected Impact:** {rec['impact']}")
                        
                        # Habit analysis
                        habit_analysis = analysis.get('habit_analysis', {})
                        if habit_analysis:
                            st.subheader("📊 Spending Habit Analysis")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                category_loyalty = habit_analysis.get('category_loyalty', 0)
                                st.metric("Category Loyalty", f"{category_loyalty:.1%}")
                                
                                if category_loyalty < 0.3:
                                    st.warning("Low category loyalty - spending is quite varied")
                                elif category_loyalty > 0.7:
                                    st.success("High category loyalty - consistent spending patterns")
                                else:
                                    st.info("Moderate category loyalty - balanced spending variety")
                            
                            with col2:
                                spending_velocity = habit_analysis.get('spending_velocity', 0)
                                st.metric("Spending Velocity", f"{spending_velocity:.1f} transactions/day")
                                
                                if spending_velocity > 5:
                                    st.warning("High transaction frequency - consider consolidating purchases")
                                elif spending_velocity < 1:
                                    st.info("Low transaction frequency - good spending control")
                                else:
                                    st.success("Moderate transaction frequency - balanced approach")
        
        except ImportError as e:
            st.error(f"❌ Advanced Markov Chain analysis not available: {e}")
            st.info("💡 Please ensure all required modules are installed for full AI functionality")
            
            # Fallback to basic analysis
            st.subheader("📊 Basic Spending Analysis")
            
            expenses_df = df[df['Amount'] < 0]
            if not expenses_df.empty:
                most_frequent_category = expenses_df['Category'].mode().iloc[0] if not expenses_df['Category'].mode().empty else 'Unknown'
                highest_spending_category = expenses_df.groupby('Category')['Amount'].sum().abs().idxmax()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Most Frequent Category", most_frequent_category)
                with col2:
                    st.metric("Highest Spending Category", highest_spending_category)
        
        except Exception as e:
            st.error(f"❌ Error in AI analysis: {e}")
            st.info("💡 Please check your data and try again")

def render_settings_section(df):
    """Render settings and configuration section"""
    st.header("⚙️ Settings & Configuration")
    
    # Sub-tabs for settings
    settings_tab1, settings_tab2 = st.tabs([
        "🏷️ Category Management", "📤 Export & Reports"
    ])
    
    with settings_tab1:
        st.subheader("🏷️ Category Management")
        
        # Show unknown/uncategorized transactions
        uncategorized = df[df['Category'] == 'Other']
        
        if not uncategorized.empty:
            st.write("**🔍 Uncategorized Transactions**")
            st.write("Assign categories to improve your analysis:")
            
            # Group by unique details for easier categorization
            unique_details = uncategorized.groupby('Details').agg({
                'Amount': 'count'
            }).rename(columns={'Amount': 'Count'}).reset_index()
            
            for i, (_, row) in enumerate(unique_details.head(20).iterrows()):
                detail = row['Details']
                count = row['Count']
                
                # Create unique key using index and hash
                unique_key = f"cat_{i}_{hash(detail) % 10000}"
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{detail}** ({count} transactions)")
                
                with col2:
                    new_category = st.selectbox(
                        f"Category for {detail[:30]}...",
                        options=['Food', 'Transport', 'Utilities', 'Entertainment', 'Shopping', 'Health', 'Education', 'Income', 'Other'],
                        key=unique_key,
                        label_visibility="collapsed"
                    )
                    
                    if st.button(f"Assign", key=f"assign_{unique_key}"):
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
    
    with settings_tab2:
        st.subheader("📤 Export & Reports")
        
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

def main():
    st.title("💰 M-Pesa Statement Analyzer")
    st.markdown("**AI-powered financial insights from your M-Pesa transactions**")
    
    # Load existing category mappings
    st.session_state.category_mappings = load_category_mappings()
    
    # Initialize components
    processor = DataProcessor()
    
    # Load income source configuration
    try:
        income_manager = IncomeSourceManager()
        income_config = income_manager.load_income_config()
        categorizer = ExpenseCategorizer(
            st.session_state.category_mappings,
            income_config.get('income_sources', {})
        )
    except:
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
            if 'Category' in df.columns:
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
        
        # Add support section to sidebar
        feedback_system.render_quick_support_sidebar()
    
    # Handle feedback popup
    if st.session_state.show_feedback:
        with st.expander("📝 Quick Feedback", expanded=True):
            feedback_system.render_feedback_form(form_key="quick_feedback_form")
            if st.button("❌ Close Feedback"):
                st.session_state.show_feedback = False
                st.rerun()
    
    # Main content area
    if st.session_state.categorized_data is not None:
        df = st.session_state.filtered_data if 'filtered_data' in st.session_state else st.session_state.categorized_data
        
        # Organized navigation with main sections
        st.markdown("---")
        
        # Main navigation
        main_tab = st.selectbox(
            "📋 Choose Analysis Section:",
            ["📊 Dashboard", "💰 Income & Budget", "🧠 AI Insights", "⚙️ Settings", "💝 Support & Community"],
            help="Select the main section you want to explore"
        )
        
        if main_tab == "📊 Dashboard":
            render_dashboard_section(df)
        elif main_tab == "💰 Income & Budget":
            render_income_budget_section(df)
        elif main_tab == "🧠 AI Insights":
            render_ai_insights_section(df)
        elif main_tab == "⚙️ Settings":
            render_settings_section(df)
        elif main_tab == "💝 Support & Community":
            feedback_system.render_complete_support_section()
    
    else:
        # Welcome screen
        st.markdown("""
        ## 🚀 Get Started
        
        Upload your M-Pesa statement (CSV or PDF format) using the sidebar to begin your comprehensive financial analysis.
        
        ### 🎯 Smart Financial Features:
        
        **📊 Dashboard**
        - **Financial Overview** with key metrics and insights
        - **Detailed Spending Analysis** with interactive charts
        - **Trend Analysis** to track patterns over time
        
        **💰 Income & Budget**
        - **Income Source Management** with AI-powered categorization
        - **Budget Coach** with personalized optimization tips
        - **Spending Benchmarks** compared to similar users
        
        **🧠 AI Insights**
        - **Predictive Analytics** for future spending forecasts
        - **Behavior Analysis** using advanced Markov Chain modeling
        - **Anomaly Detection** for unusual spending patterns
        
        **⚙️ Settings**
        - **Category Management** for transaction categorization
        - **Export & Reports** for data download and sharing
        
        ### 📱 Supported Formats:
        - **CSV files** from M-Pesa statement downloads
        - **PDF files** with automatic text extraction
        
        ### 🔒 Privacy & Security:
        - All analysis is performed locally on your device
        - No data is stored or transmitted to external servers
        - Your financial information remains completely private
        """)

if __name__ == "__main__":
    main()