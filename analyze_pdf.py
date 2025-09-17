import pdfplumber
import pandas as pd
import re

def analyze_mpesa_pdf(pdf_path):
    """Analyze M-Pesa PDF statement structure"""
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        # Extract text from first few pages
        for i, page in enumerate(pdf.pages[:3]):  # First 3 pages
            print(f"\n{'='*50}")
            print(f"PAGE {i+1} TEXT")
            print(f"{'='*50}")
            text = page.extract_text()
            if text:
                print(text[:1500])  # First 1500 characters
            
            # Try to extract tables
            tables = page.extract_tables()
            if tables:
                print(f"\n--- TABLES ON PAGE {i+1} ---")
                for j, table in enumerate(tables):
                    print(f"Table {j+1}:")
                    for row in table[:5]:  # First 5 rows
                        print(row)
                    print("...")

if __name__ == "__main__":
    analyze_mpesa_pdf("Mpesa Statement.pdf")