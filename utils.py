import pandas as pd
import io
from datetime import datetime

def export_to_csv(df: pd.DataFrame) -> str:
    """Export DataFrame to CSV string"""
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()

def export_summary_to_pdf(summary_data: dict) -> bytes:
    """Export summary data to PDF (placeholder implementation)"""
    # This is a placeholder - you would implement actual PDF generation here
    # For now, return a simple text representation
    summary_text = f"""
M-PESA STATEMENT ANALYSIS SUMMARY
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW:
- Analysis Period: {summary_data.get('date_range', 'N/A')}
- Total Transactions: {summary_data.get('total_transactions', 0)}
- Total Amount Spent: KSh {summary_data.get('total_spent', 0):,.2f}

CATEGORY BREAKDOWN:
"""
    
    if 'category_breakdown' in summary_data:
        for category, amount in sorted(summary_data['category_breakdown'].items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / summary_data.get('total_spent', 1) * 100)
            summary_text += f"- {category}: KSh {amount:,.2f} ({percentage:.1f}%)\n"
    
    return summary_text.encode('utf-8')