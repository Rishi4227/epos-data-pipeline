"""
Useful SQL queries for EPOS analytics
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker
import pandas as pd
from config.database_config import get_connection_string, DEFAULT_DB_TYPE
from sql.models import Transaction, Location, Product, Employee

engine = create_engine(get_connection_string(DEFAULT_DB_TYPE))
Session = sessionmaker(bind=engine)


def check_table_has_data(table_name):
    """Check if a table has data"""
    session = Session()
    try:
        result = session.execute(text(f"SELECT COUNT(*) as count FROM {table_name}")).fetchone()
        return result[0] > 0 if result else False
    finally:
        session.close()


def daily_sales_report(start_date=None, end_date=None):
    """Daily sales aggregation"""
    session = Session()
    
    query = """
    SELECT 
        transaction_date,
        COUNT(*) as transaction_count,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_transaction_value,
        SUM(CASE WHEN transaction_status = 'completed' THEN total_amount ELSE 0 END) as completed_revenue,
        SUM(CASE WHEN transaction_status = 'refunded' THEN total_amount ELSE 0 END) as refunded_amount
    FROM transactions
    GROUP BY transaction_date
    ORDER BY transaction_date
    """
    
    df = pd.read_sql(query, engine)
    session.close()
    return df


def location_performance():
    """Performance by location"""
    session = Session()
    
    query = """
    SELECT 
        l.location_name,
        l.city,
        l.location_type,
        COUNT(t.transaction_id) as transaction_count,
        SUM(t.total_amount) as total_revenue,
        AVG(t.total_amount) as avg_transaction_value,
        SUM(t.tip_amount) as total_tips
    FROM locations l
    LEFT JOIN transactions t ON l.location_id = t.location_id
    WHERE t.transaction_status = 'completed'
    GROUP BY l.location_id, l.location_name, l.city, l.location_type
    ORDER BY total_revenue DESC
    """
    
    df = pd.read_sql(query, engine)
    session.close()
    return df


def product_category_analysis():
    """Sales by product category"""
    session = Session()
    
    # Check if we have transaction items data
    has_transaction_items = check_table_has_data('transaction_items')
    
    if has_transaction_items:
        query = """
        SELECT 
            COALESCE(p.product_category, 'Uncategorized') as product_category,
            COUNT(DISTINCT t.transaction_id) as transaction_count,
            SUM(ti.item_total) as total_revenue,
            AVG(ti.item_total) as avg_price,
            SUM(ti.quantity) as total_quantity
        FROM transaction_items ti
        JOIN transactions t ON ti.transaction_id = t.transaction_id
        LEFT JOIN products p ON ti.product_id = p.product_id
        WHERE t.transaction_status = 'completed'
        GROUP BY COALESCE(p.product_category, 'Uncategorized')
        ORDER BY total_revenue DESC
        """
    else:
        # Fallback to transaction-level analysis only
        query = """
        SELECT 
            'All Products (Transaction-level)' as product_category,
            COUNT(*) as transaction_count,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_price,
            SUM(num_items) as total_quantity
        FROM transactions
        WHERE transaction_status = 'completed'
        """
    
    df = pd.read_sql(query, engine)
    session.close()
    return df


def hourly_sales_pattern():
    """Sales patterns by hour"""
    session = Session()
    
    query = """
    SELECT 
        CAST(strftime('%H', timestamp) AS INTEGER) as hour,
        COUNT(*) as transaction_count,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_transaction_value
    FROM transactions
    WHERE transaction_status = 'completed'
    GROUP BY hour
    ORDER BY hour
    """
    
    df = pd.read_sql(query, engine)
    session.close()
    return df


def employee_performance():
    """Employee sales performance"""
    session = Session()
    
    query = """
    SELECT 
        e.employee_id,
        e.first_name || ' ' || e.last_name as employee_name,
        e.role,
        COUNT(t.transaction_id) as transaction_count,
        SUM(t.total_amount) as total_revenue,
        AVG(t.total_amount) as avg_transaction_value,
        SUM(CASE WHEN t.transaction_status = 'refunded' THEN 1 ELSE 0 END) as refund_count
    FROM employees e
    LEFT JOIN transactions t ON e.employee_id = t.employee_id
    WHERE t.transaction_status IN ('completed', 'refunded')
    GROUP BY e.employee_id, employee_name, e.role
    ORDER BY total_revenue DESC
    """
    
    df = pd.read_sql(query, engine)
    session.close()
    return df


def payment_method_breakdown():
    """Payment method distribution"""
    session = Session()
    
    query = """
    SELECT 
        payment_method,
        COUNT(*) as transaction_count,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_transaction_value,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions WHERE transaction_status = 'completed'), 2) as percentage
    FROM transactions
    WHERE transaction_status = 'completed'
    GROUP BY payment_method
    ORDER BY transaction_count DESC
    """
    
    df = pd.read_sql(query, engine)
    session.close()
    return df


def top_performing_products():
    """Top 20 products by revenue"""
    session = Session()
    
    # Check if we have transaction items data
    has_transaction_items = check_table_has_data('transaction_items')
    
    if has_transaction_items:
        query = """
        SELECT 
            p.product_name,
            p.product_category,
            COUNT(ti.item_id) as times_sold,
            SUM(ti.quantity) as total_quantity,
            SUM(ti.item_total) as total_revenue,
            AVG(ti.item_total) as avg_price
        FROM transaction_items ti
        JOIN transactions t ON ti.transaction_id = t.transaction_id
        JOIN products p ON ti.product_id = p.product_id
        WHERE t.transaction_status = 'completed'
        GROUP BY p.product_id, p.product_name, p.product_category
        ORDER BY total_revenue DESC
        LIMIT 20
        """
    else:
        # Fallback: Show transaction statistics
        query = """
        SELECT 
            'Product-level data not available' as product_name,
            'See transaction-level reports' as product_category,
            COUNT(*) as times_sold,
            SUM(num_items) as total_quantity,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_price
        FROM transactions
        WHERE transaction_status = 'completed'
        LIMIT 1
        """
    
    df = pd.read_sql(query, engine)
    session.close()
    return df


def refund_analysis():
    """Analyze refund patterns"""
    session = Session()
    
    query = """
    SELECT 
        l.location_name,
        COUNT(*) as refund_count,
        SUM(t.total_amount) as refund_amount,
        AVG(t.total_amount) as avg_refund_value
    FROM transactions t
    JOIN locations l ON t.location_id = l.location_id
    WHERE t.transaction_status = 'refunded'
    GROUP BY l.location_id, l.location_name
    ORDER BY refund_count DESC
    """
    
    df = pd.read_sql(query, engine)
    session.close()
    return df


def monthly_revenue_trend():
    """Monthly revenue trends"""
    session = Session()
    
    query = """
    SELECT 
        strftime('%Y-%m', transaction_date) as month,
        COUNT(*) as transaction_count,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_transaction_value
    FROM transactions
    WHERE transaction_status = 'completed'
    GROUP BY month
    ORDER BY month
    """
    
    df = pd.read_sql(query, engine)
    session.close()
    return df


if __name__ == "__main__":
    print("\n" + "="*60)
    print("EPOS DATABASE QUERIES")
    print("="*60 + "\n")
    
    # Check data availability
    print("DATA AVAILABILITY CHECK:")
    print(f"  Transactions: {check_table_has_data('transactions')}")
    print(f"  Transaction Items: {check_table_has_data('transaction_items')}")
    print(f"  Products: {check_table_has_data('products')}")
    print()
    
    # Run all queries and display results
    print("1. DAILY SALES REPORT (Last 10 Days)")
    print(daily_sales_report().tail(10))
    print("\n" + "-"*60 + "\n")
    
    print("2. LOCATION PERFORMANCE")
    print(location_performance())
    print("\n" + "-"*60 + "\n")
    
    print("3. PRODUCT CATEGORY ANALYSIS")
    print(product_category_analysis())
    print("\n" + "-"*60 + "\n")
    
    print("4. HOURLY SALES PATTERN")
    print(hourly_sales_pattern())
    print("\n" + "-"*60 + "\n")
    
    print("5. EMPLOYEE PERFORMANCE (Top 10)")
    print(employee_performance().head(10))
    print("\n" + "-"*60 + "\n")
    
    print("6. PAYMENT METHOD BREAKDOWN")
    print(payment_method_breakdown())
    print("\n" + "-"*60 + "\n")
    
    print("7. TOP PERFORMING PRODUCTS")
    print(top_performing_products())
    print("\n" + "-"*60 + "\n")
    
    print("8. REFUND ANALYSIS")
    print(refund_analysis())
    print("\n" + "-"*60 + "\n")
    
    print("9. MONTHLY REVENUE TREND")
    print(monthly_revenue_trend())
    print("\n" + "="*60 + "\n")