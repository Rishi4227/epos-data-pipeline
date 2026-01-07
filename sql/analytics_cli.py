"""
Command-line analytics tool for EPOS data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from sql.queries import *


def display_report(report_name, df):
    """Display a formatted report"""
    print("\n" + "="*80)
    print(f"  {report_name.upper()}")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(description='EPOS Analytics CLI')
    parser.add_argument('report', choices=[
        'daily', 'location', 'category', 'hourly', 'employee', 
        'payment', 'products', 'refunds', 'monthly', 'all'
    ], help='Report type to generate')
    
    args = parser.parse_args()
    
    reports = {
        'daily': ('Daily Sales Report', daily_sales_report),
        'location': ('Location Performance', location_performance),
        'category': ('Product Category Analysis', product_category_analysis),
        'hourly': ('Hourly Sales Pattern', hourly_sales_pattern),
        'employee': ('Employee Performance', employee_performance),
        'payment': ('Payment Method Breakdown', payment_method_breakdown),
        'products': ('Top Performing Products', top_performing_products),
        'refunds': ('Refund Analysis', refund_analysis),
        'monthly': ('Monthly Revenue Trend', monthly_revenue_trend)
    }
    
    if args.report == 'all':
        for name, func in reports.values():
            df = func()
            display_report(name, df)
    else:
        name, func = reports[args.report]
        df = func()
        display_report(name, df)
        
        # Save to CSV
        output_file = f'data/processed/{args.report}_report.csv'
        df.to_csv(output_file, index=False)
        print(f"✅ Report saved to: {output_file}")


if __name__ == "__main__":
    main()