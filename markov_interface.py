import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List

from behavior_analyzer import BehaviorAnalyzer
from markov_predictor import MarkovChainPredictor

class MarkovInterface:
    """Streamlit interface for Markov Chain behavior analysis"""
    
    def __init__(self):
        self.analyzer = BehaviorAnalyzer()
    
    def render_markov_analysis(self, df: pd.DataFrame):
        """Render the complete Markov Chain analysis interface"""
        if df.empty:
            st.warning("No transaction data available for behavior analysis")
            return
        
        st.subheader("🧠 AI-Powered Behavior Analysis")
        st.write("Using Markov Chains to model your spending patterns and predict future behavior")
        
        # Analysis tabs
        analysis_tab1, analysis_tab2, analysis_tab3, analysis_tab4 = st.tabs([
            "🔮 Predictions", "📊 Behavior Patterns", "⚠️ Anomaly Detection", "💡 Insights & Tips"
        ])
        
        # Perform analysis (cached for performance)
        with st.spinner("🧠 Analyzing spending behavior with AI..."):
            analysis = self._get_cached_analysis(df)
        
        with analysis_tab1:
            self._render_predictions_tab(analysis)
        
        with analysis_tab2:
            self._render_patterns_tab(analysis)
        
        with analysis_tab3:
            self._render_anomalies_tab(analysis)
        
        with analysis_tab4:
            self._render_insights_tab(analysis)
    
    @st.cache_data
    def _get_cached_analysis(_self, df: pd.DataFrame) -> Dict:
        """Cached analysis to avoid recomputation"""
        analyzer = BehaviorAnalyzer()
        return analyzer.analyze_behavior(df)
    
    def _render_predictions_tab(self, analysis: Dict):
        """Render predictions tab"""
        st.subheader("🔮 Spending Predictions")
        
        predictions = analysis.get('spending_predictions', {})
        
        # Model statistics
        col1, col2, col3, col4 = st.columns(4)
        
        model_stats = self.analyzer.markov_model.get_model_stats()
        
        with col1:
            st.metric("Model Status", model_stats.get('status', 'Unknown'))
        
        with col2:
            st.metric("States Learned", model_stats.get('total_states', 0))
        
        with col3:
            st.metric("Transitions", model_stats.get('total_transitions', 0))
        
        with col4:
            st.metric("Patterns Found", model_stats.get('behavioral_patterns', 0))
        
        # Monthly spending forecast
        st.subheader("📈 Monthly Spending Forecast")
        monthly_forecast = predictions.get('monthly_forecast', {})
        
        if monthly_forecast:
            forecast_data = []
            for category, data in monthly_forecast.items():
                forecast_data.append({
                    'Category': category,
                    'Predicted Amount': data['predicted_amount'],
                    'Lower Bound': data['confidence_interval'][0],
                    'Upper Bound': data['confidence_interval'][1],
                    'Expected Transactions': data['transaction_count']
                })
            
            forecast_df = pd.DataFrame(forecast_data)
            
            # Visualization
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
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Forecast table
            st.write("**Detailed Forecast:**")
            forecast_display = forecast_df.copy()
            for col in ['Predicted Amount', 'Lower Bound', 'Upper Bound']:
                forecast_display[col] = forecast_display[col].apply(lambda x: f"KSh {x:,.0f}")
            st.dataframe(forecast_display, use_container_width=True)
        
        # Next transaction predictions
        st.subheader("🎯 Next Transaction Predictions")
        
        category_predictions = {k: v for k, v in predictions.items() 
                              if k not in ['spending_sequences', 'monthly_forecast']}
        
        if category_predictions:
            selected_category = st.selectbox(
                "Select category for next transaction prediction:",
                list(category_predictions.keys())
            )
            
            if selected_category and category_predictions[selected_category]:
                next_predictions = category_predictions[selected_category]
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Prediction chart
                    pred_data = pd.DataFrame(next_predictions)
                    
                    fig = px.bar(
                        pred_data,
                        x='probability',
                        y='category',
                        orientation='h',
                        title=f"Next Transaction Predictions for {selected_category}",
                        color='confidence',
                        color_discrete_map={
                            'High': 'green',
                            'Medium': 'orange',
                            'Low': 'red',
                            'Very Low': 'darkred'
                        }
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.write("**Prediction Details:**")
                    for pred in next_predictions[:5]:
                        with st.expander(f"{pred['category']} ({pred['probability']:.1%})"):
                            st.write(f"**Confidence:** {pred['confidence']}")
                            st.write(f"**Amount Range:** {pred['amount_range']}")
                            st.write(f"**Time Period:** {pred['time_period']}")
        
        # Spending sequences
        st.subheader("🔄 Predicted Spending Sequences")
        
        sequences = predictions.get('spending_sequences', {})
        if sequences:
            for category, sequence_list in sequences.items():
                if sequence_list:
                    sequence_data = sequence_list[0]
                    sequence = sequence_data['sequence']
                    probability = sequence_data['overall_probability']
                    
                    st.write(f"**Starting with {category}:**")
                    sequence_str = " → ".join(sequence)
                    st.write(f"Likely sequence: {sequence_str}")
                    st.write(f"Probability: {probability:.1%}")
                    st.write("---")
    
    def _render_patterns_tab(self, analysis: Dict):
        """Render behavior patterns tab"""
        st.subheader("📊 Behavioral Patterns")
        
        patterns = analysis.get('behavioral_patterns', {})
        
        # Behavior score
        dashboard = self.analyzer.create_behavior_dashboard(analysis)
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
            
            # Transition network visualization
            self._create_transition_network(transitions[:8])
        
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
        
        # Category preferences
        st.subheader("📈 Category Transition Preferences")
        
        category_prefs = patterns.get('category_preferences', {})
        if category_prefs:
            pref_data = []
            for category, data in category_prefs.items():
                most_likely = data.get('most_likely_next', [])
                entropy = data.get('transition_entropy', 0)
                
                if most_likely:
                    next_cat = most_likely[0][0]
                    probability = most_likely[0][1]
                    
                    pref_data.append({
                        'Category': category,
                        'Most Likely Next': next_cat,
                        'Probability': f"{probability:.1%}",
                        'Predictability': f"{(1-entropy/2):.1%}" if entropy > 0 else "100%"
                    })
            
            if pref_data:
                pref_df = pd.DataFrame(pref_data)
                st.dataframe(pref_df, use_container_width=True)
    
    def _render_anomalies_tab(self, analysis: Dict):
        """Render anomaly detection tab"""
        st.subheader("⚠️ Anomaly Detection")
        
        anomaly_data = analysis.get('anomaly_detection', {})
        
        # Anomaly summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Anomalies", anomaly_data.get('total_anomalies', 0))
        
        with col2:
            st.metric("Anomaly Rate", f"{anomaly_data.get('anomaly_rate', 0):.1f}%")
        
        with col3:
            high_risk = len(anomaly_data.get('high_risk_anomalies', []))
            st.metric("High Risk", high_risk)
        
        with col4:
            categories_affected = len(anomaly_data.get('anomaly_categories', {}))
            st.metric("Categories Affected", categories_affected)
        
        # Anomaly categories breakdown
        anomaly_categories = anomaly_data.get('anomaly_categories', {})
        if anomaly_categories:
            st.subheader("📊 Anomalies by Category")
            
            fig = px.pie(
                values=list(anomaly_categories.values()),
                names=list(anomaly_categories.keys()),
                title="Distribution of Anomalies by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # High-risk anomalies
        high_risk_anomalies = anomaly_data.get('high_risk_anomalies', [])
        if high_risk_anomalies:
            st.subheader("🚨 High-Risk Anomalies")
            st.write("These transactions are highly unusual based on your spending patterns:")
            
            for anomaly in high_risk_anomalies[:10]:
                with st.expander(f"{anomaly['date']} - {anomaly['category']} - KSh {anomaly['amount']:,.0f}"):
                    st.write(f"**Transaction:** {anomaly['details']}")
                    st.write(f"**Anomaly Score:** {anomaly['anomaly_score']:.1%}")
                    st.write(f"**Reason:** {anomaly['reason']}")
                    
                    # Risk level indicator
                    if anomaly['anomaly_score'] > 0.9:
                        st.error("🔴 Very High Risk")
                    elif anomaly['anomaly_score'] > 0.8:
                        st.warning("🟡 High Risk")
                    else:
                        st.info("🔵 Medium Risk")
        
        # All anomalies table
        all_anomalies = anomaly_data.get('anomalies', [])
        if all_anomalies:
            st.subheader("📋 All Detected Anomalies")
            
            anomaly_df = pd.DataFrame(all_anomalies)
            if not anomaly_df.empty:
                # Format for display
                display_df = anomaly_df[['date', 'category', 'amount', 'anomaly_score', 'reason']].copy()
                display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
                display_df['amount'] = display_df['amount'].apply(lambda x: f"KSh {x:,.0f}")
                display_df['anomaly_score'] = display_df['anomaly_score'].apply(lambda x: f"{x:.1%}")
                
                st.dataframe(display_df, use_container_width=True)
    
    def _render_insights_tab(self, analysis: Dict):
        """Render insights and recommendations tab"""
        st.subheader("💡 AI-Generated Insights & Recommendations")
        
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
                    
                    # Create risk indicator
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
            st.subheader("🎯 Personalized Recommendations")
            
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
    
    def _create_transition_network(self, transitions: List[Dict]):
        """Create a network visualization of state transitions"""
        st.subheader("🕸️ Spending Transition Network")
        
        # Create network data
        nodes = set()
        edges = []
        
        for trans in transitions:
            from_state = trans['from_state'].split('_')[0]  # Get category only
            to_state = trans['to_state'].split('_')[0]
            probability = trans['probability']
            
            nodes.add(from_state)
            nodes.add(to_state)
            edges.append((from_state, to_state, probability))
        
        # Create a simple network representation
        st.write("**Top Spending Transitions:**")
        for from_state, to_state, prob in edges:
            st.write(f"• {from_state} → {to_state} ({prob:.1%})")
    
    def render_model_configuration(self):
        """Render model configuration options"""
        st.subheader("⚙️ Model Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            order = st.selectbox(
                "Markov Chain Order",
                options=[1, 2, 3],
                value=2,
                help="Higher order captures more complex patterns but requires more data"
            )
        
        with col2:
            anomaly_threshold = st.slider(
                "Anomaly Detection Threshold",
                min_value=0.01,
                max_value=0.5,
                value=0.1,
                step=0.01,
                help="Lower values detect more anomalies"
            )
        
        if st.button("Update Model Configuration"):
            self.analyzer.markov_model = MarkovChainPredictor(order=order)
            st.success("Model configuration updated!")
            st.rerun()