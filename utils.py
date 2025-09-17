import pandas as pd
import io
from datetime import datetime
import json

def export_to_csv(df: pd.DataFrame) -> str:
    """Export DataFrame to CSV format"""
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()

def export_summary_to_pdf(summary_data: dict) -> str:
    """Generate a summary report in text format"""
    report = f"""
M-PESA STATEMENT ANALYSIS SUMMARY
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW:
- Analysis Period: {summary_data.get('date_range', 'N/A')}
- Total Transactions: {summary_data.get('total_transactions', 0)}
- Total Amount Spent: KSh {summary_data.get('total_spent', 0):,.2f}

CATEGORY BREAKDOWN:
"""
    
    category_breakdown = summary_data.get('category_breakdown', {})
    total_spent = summary_data.get('total_spent', 0)
    
    for category, amount in sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / total_spent * 100) if total_spent > 0 else 0
        report += f"- {category}: KSh {amount:,.2f} ({percentage:.1f}%)\n"
    
    return report

def format_currency(amount: float) -> str:
    """Format amount as Kenyan Shillings"""
    return f"KSh {amount:,.2f}"

def calculate_month_over_month_change(current: float, previous: float) -> dict:
    """Calculate month-over-month change"""
    if previous == 0:
        return {
            'change_amount': current,
            'change_percentage': 100.0 if current > 0 else 0.0,
            'direction': 'increased' if current > 0 else 'no change'
        }
    
    change_amount = current - previous
    change_percentage = (change_amount / previous) * 100
    direction = 'increased' if change_amount > 0 else 'decreased' if change_amount < 0 else 'no change'
    
    return {
        'change_amount': abs(change_amount),
        'change_percentage': abs(change_percentage),
        'direction': direction
    }

def get_spending_insights(df: pd.DataFrame) -> list:
    """Generate spending insights from transaction data"""
    insights = []
    
    # Filter for expenses only
    expenses_df = df[df['Amount'] < 0].copy()
    expenses_df['Amount'] = expenses_df['Amount'].abs()
    
    if expenses_df.empty:
        return ["No expense transactions found."]
    
    # Top spending category
    category_totals = expenses_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
    total_expenses = category_totals.sum()
    
    if not category_totals.empty:
        top_category = category_totals.index[0]
        top_amount = category_totals.iloc[0]
        top_percentage = (top_amount / total_expenses * 100)
        insights.append(f"Your biggest spending category is {top_category} at {format_currency(top_amount)} ({top_percentage:.1f}% of total expenses)")
    
    # High-frequency transactions
    transaction_counts = expenses_df.groupby('Details').size().sort_values(ascending=False)
    if not transaction_counts.empty:
        most_frequent = transaction_counts.index[0]
        frequency = transaction_counts.iloc[0]
        if frequency > 1:
            insights.append(f"Your most frequent transaction is '{most_frequent}' with {frequency} occurrences")
    
    # Large transactions
    large_threshold = expenses_df['Amount'].quantile(0.9)
    large_transactions = expenses_df[expenses_df['Amount'] >= large_threshold]
    if not large_transactions.empty:
        insights.append(f"You have {len(large_transactions)} large transactions (over {format_currency(large_threshold)})")
    
    # Weekend vs weekday spending
    if 'Date' in expenses_df.columns:
        expenses_df['is_weekend'] = expenses_df['Date'].dt.weekday >= 5
        weekend_spending = expenses_df[expenses_df['is_weekend']]['Amount'].sum()
        weekday_spending = expenses_df[~expenses_df['is_weekend']]['Amount'].sum()
        
        if weekend_spending > 0 and weekday_spending > 0:
            if weekend_spending > weekday_spending:
                insights.append("You tend to spend more on weekends than weekdays")
            else:
                insights.append("You tend to spend more on weekdays than weekends")
    
    return insights

def validate_mpesa_data(df: pd.DataFrame) -> dict:
    """Validate if the uploaded data appears to be M-Pesa transaction data"""
    validation_result = {
        'is_valid': False,
        'issues': [],
        'confidence': 0
    }
    
    # Check for required columns
    required_columns = ['Date', 'Details', 'Amount']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        validation_result['issues'].append(f"Missing required columns: {', '.join(missing_columns)}")
        return validation_result
    
    # Check for M-Pesa specific patterns in details
    mpesa_keywords = [
        'sent to', 'received from', 'buy goods', 'pay bill', 'withdraw',
        'agent', 'airtime', 'safaricom', 'mpesa', 'paybill', 'till'
    ]
    
    details_text = ' '.join(df['Details'].astype(str).str.lower())
    keyword_matches = sum(1 for keyword in mpesa_keywords if keyword in details_text)
    
    validation_result['confidence'] = min((keyword_matches / len(mpesa_keywords)) * 100, 100)
    
    if validation_result['confidence'] >= 30:
        validation_result['is_valid'] = True
    else:
        validation_result['issues'].append("Data doesn't appear to contain M-Pesa transaction patterns")
    
    # Check data quality
    if df['Amount'].isna().sum() > len(df) * 0.5:
        validation_result['issues'].append("Too many missing amount values")
    
    if df['Details'].isna().sum() > len(df) * 0.3:
        validation_result['issues'].append("Too many missing transaction details")
    
    return validation_result

def clean_transaction_details(details: str) -> str:
    """Clean and standardize transaction details"""
    if pd.isna(details):
        return ""
    
    # Convert to string and strip whitespace
    details = str(details).strip()
    
    # Remove extra spaces
    details = ' '.join(details.split())
    
    # Common cleaning patterns
    # Remove reference numbers but keep important identifiers
    details = details.replace('Transaction ID:', '')
    details = details.replace('Ref:', '')
    
    return details

def categorize_unknown_transaction(details: str, amount: float, existing_mappings: dict) -> str:
    """Suggest category for unknown transaction"""
    details_lower = details.lower()
    
    # Check existing mappings for similar transactions
    for mapped_detail, category in existing_mappings.items():
        # Simple similarity check
        mapped_words = set(mapped_detail.lower().split())
        detail_words = set(details_lower.split())
        
        # If there's significant word overlap, suggest the same category
        overlap = len(mapped_words.intersection(detail_words))
        if overlap >= min(2, len(mapped_words) * 0.5):
            return category
    
    # Amount-based suggestions
    if abs(amount) > 10000:  # Large amounts
        if any(word in details_lower for word in ['pay', 'bill', 'payment']):
            return 'Utilities'
        else:
            return 'Shopping'
    elif abs(amount) < 500:  # Small amounts
        if any(word in details_lower for word in ['food', 'snack', 'drink']):
            return 'Food'
        else:
            return 'Transport'
    
    return 'Other'
