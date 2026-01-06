"""
Quick data verification and exploration script
"""

import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.data_config import OUTPUT_DIR

def verify_data():
    """Verify generated data quality"""
    
    print("\n" + "="*60)
    print("DATA VERIFICATION REPORT")
    print("="*60)
    
    # Load data
    print("\n📂 Loading data files...")
    transactions = pd.read_parquet(f'{OUTPUT_DIR}/epos_transactions.parquet')
    locations = pd.read_csv(f'{OUTPUT_DIR}/locations.csv')
    products = pd.read_csv(f'{OUTPUT_DIR}/products.csv')
    employees = pd.read_csv(f'{OUTPUT_DIR}/employees.csv')
    
    print(f"✅ Transactions: {len(transactions):,} rows")
    print(f"✅ Locations: {len(locations):,} rows")
    print(f"✅ Products: {len(products):,} rows")
    print(f"✅ Employees: {len(employees):,} rows")
    
    # Check for nulls
    print("\n🔍 Checking for null values...")
    null_counts = transactions.isnull().sum()
    if null_counts.sum() == 0:
        print("✅ No unexpected null values found")
    else:
        print("⚠️  Null values found:")
        print(null_counts[null_counts > 0])
    
    # Data types
    print("\n📊 Sample transaction data:")
    print(transactions.head(3)[['transaction_id', 'timestamp', 'location_name', 
                                 'product_category', 'total_amount', 'transaction_status']])
    
    # Time distribution
    print("\n⏰ Transactions by hour:")
    transactions['hour'] = pd.to_datetime(transactions['timestamp']).dt.hour
    hourly = transactions.groupby('hour').size()
    print(hourly)
    
    # Location distribution
    print("\n📍 Transactions by location:")
    print(transactions['location_name'].value_counts())
    
    # Revenue by status
    print("\n💰 Revenue by transaction status:")
    revenue_by_status = transactions.groupby('transaction_status')['total_amount'].agg(['sum', 'count', 'mean'])
    revenue_by_status['sum'] = revenue_by_status['sum'].apply(lambda x: f"£{x:,.2f}")
    revenue_by_status['mean'] = revenue_by_status['mean'].apply(lambda x: f"£{x:.2f}")
    print(revenue_by_status)
    
    # Check for refunds
    print("\n🔄 Refund analysis:")
    refunds = transactions[transactions['transaction_status'] == 'refunded']
    print(f"Total refunds: {len(refunds):,}")
    print(f"Refund amount: £{refunds['total_amount'].sum():,.2f}")
    print(f"Average refund: £{refunds['total_amount'].mean():.2f}")
    
    # Check for errors
    print("\n❌ Error analysis:")
    errors = transactions[transactions['transaction_status'] == 'error']
    print(f"Total errors: {len(errors):,}")
    print(f"Error rate: {len(errors)/len(transactions)*100:.2f}%")
    
    # Payment methods
    print("\n💳 Payment method breakdown:")
    payment_dist = transactions['payment_method'].value_counts()
    for method, count in payment_dist.items():
        pct = count / len(transactions) * 100
        print(f"{method:20s}: {count:6,} ({pct:5.2f}%)")
    
    # Date range
    print("\n📅 Date coverage:")
    print(f"Start: {transactions['transaction_date'].min()}")
    print(f"End: {transactions['transaction_date'].max()}")
    print(f"Days covered: {transactions['transaction_date'].nunique()}")
    
    # File sizes
    print("\n💾 File sizes:")
    csv_size = os.path.getsize(f'{OUTPUT_DIR}/epos_transactions.csv') / (1024*1024)
    parquet_size = os.path.getsize(f'{OUTPUT_DIR}/epos_transactions.parquet') / (1024*1024)
    print(f"CSV: {csv_size:.2f} MB")
    print(f"Parquet: {parquet_size:.2f} MB")
    print(f"Compression ratio: {csv_size/parquet_size:.2f}x")
    
    print("\n" + "="*60)
    print("✅ DATA VERIFICATION COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    verify_data()