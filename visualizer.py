import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List

def create_pie_chart(data: pd.DataFrame, labels_col: str, values_col: str, title: str):
    """Create an interactive pie chart"""
    fig = px.pie(
        data, 
        values=values_col, 
        names=labels_col,
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Amount: KSh %{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=True,
        height=500,
        font=dict(size=12)
    )
    
    return fig

def create_bar_chart(data: pd.DataFrame, x_col: str, y_col: str, title: str):
    """Create an interactive bar chart"""
    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        title=title,
        color=y_col,
        color_continuous_scale='viridis'
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Amount: KSh %{y:,.2f}<extra></extra>'
    )
    
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=f'Amount (KSh)',
        height=500,
        xaxis_tickangle=-45,
        font=dict(size=12)
    )
    
    return fig

def create_trend_chart(data: pd.DataFrame, x_col: str, y_col: str, color_col: str, title: str):
    """Create a line chart for trends over time"""
    fig = px.line(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        markers=True
    )
    
    fig.update_traces(
        hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Amount: KSh %{y:,.2f}<extra></extra>'
    )
    
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Amount (KSh)',
        height=500,
        font=dict(size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_monthly_comparison(data: pd.DataFrame, x_col: str, y_col: str, title: str):
    """Create a bar chart comparing monthly totals"""
    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        title=title,
        color=y_col,
        color_continuous_scale='blues'
    )
    
    # Add trend line
    fig.add_trace(
        go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode='lines+markers',
            name='Trend',
            line=dict(color='red', width=2),
            hovertemplate='<b>Trend</b><br>Date: %{x}<br>Amount: KSh %{y:,.2f}<extra></extra>'
        )
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Total Spent: KSh %{y:,.2f}<extra></extra>',
        selector=dict(type='bar')
    )
    
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Total Spent (KSh)',
        height=500,
        font=dict(size=12)
    )
    
    return fig

def create_category_distribution(data: pd.DataFrame, title: str):
    """Create a horizontal bar chart for category distribution"""
    fig = px.bar(
        data,
        x='Amount',
        y='Category',
        orientation='h',
        title=title,
        color='Amount',
        color_continuous_scale='viridis'
    )
    
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Amount: KSh %{x:,.2f}<extra></extra>'
    )
    
    fig.update_layout(
        xaxis_title='Amount (KSh)',
        yaxis_title='Category',
        height=600,
        font=dict(size=12)
    )
    
    return fig

def create_daily_spending_heatmap(data: pd.DataFrame, title: str):
    """Create a heatmap showing daily spending patterns"""
    # Prepare data for heatmap
    data_copy = data.copy()
    data_copy['Weekday'] = data_copy['Date'].dt.day_name()
    data_copy['Week'] = data_copy['Date'].dt.isocalendar().week
    
    # Filter for expenses only
    expenses = data_copy[data_copy['Amount'] < 0].copy()
    expenses['Amount'] = expenses['Amount'].abs()
    
    # Create pivot table
    heatmap_data = expenses.pivot_table(
        values='Amount',
        index='Weekday',
        columns='Week',
        aggfunc='sum',
        fill_value=0
    )
    
    # Reorder days of week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data.reindex(day_order)
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='viridis',
        hovertemplate='<b>Week %{x}, %{y}</b><br>Total Spent: KSh %{z:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Week of Year',
        yaxis_title='Day of Week',
        height=400,
        font=dict(size=12)
    )
    
    return fig

def create_transaction_volume_chart(data: pd.DataFrame, title: str):
    """Create a chart showing transaction volume over time"""
    daily_counts = data.groupby(data['Date'].dt.date).size().reset_index()
    daily_counts.columns = ['Date', 'Transaction_Count']
    
    fig = px.line(
        daily_counts,
        x='Date',
        y='Transaction_Count',
        title=title,
        markers=True
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Transactions: %{y}<extra></extra>'
    )
    
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Number of Transactions',
        height=400,
        font=dict(size=12)
    )
    
    return fig
