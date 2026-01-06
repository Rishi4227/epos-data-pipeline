"""
Configuration for EPOS data generation
"""

# Data generation parameters
NUM_TRANSACTIONS = 100000
NUM_LOCATIONS = 8
NUM_PRODUCTS = 150
NUM_EMPLOYEES = 25

# Date range for transactions
START_DATE = "2024-01-01"
END_DATE = "2024-12-31"

# Business hours (24-hour format)
BUSINESS_HOURS = {
    'open': 10,   # 10 AM
    'close': 23   # 11 PM
}

# Transaction status distribution (%)
TRANSACTION_STATUS_DISTRIBUTION = {
    'completed': 92.0,
    'refunded': 5.0,
    'voided': 2.0,
    'error': 1.0
}

# Payment method distribution (%)
PAYMENT_METHOD_DISTRIBUTION = {
    'credit_card': 45.0,
    'debit_card': 30.0,
    'cash': 15.0,
    'mobile_payment': 8.0,
    'gift_card': 2.0
}

# Product categories for bars/restaurants
PRODUCT_CATEGORIES = [
    'Beer',
    'Wine',
    'Spirits',
    'Cocktails',
    'Soft Drinks',
    'Appetizers',
    'Main Course',
    'Desserts',
    'Sides',
    'Hot Beverages'
]

# Location details
LOCATIONS = [
    {
        'name': 'Downtown Taproom',
        'type': 'bar',
        'city': 'Manchester',
        'timezone': 'Europe/London'
    },
    {
        'name': 'Riverside Bistro',
        'type': 'restaurant',
        'city': 'Bristol',
        'timezone': 'Europe/London'
    },
    {
        'name': 'The Oak & Barrel',
        'type': 'pub',
        'city': 'Leeds',
        'timezone': 'Europe/London'
    },
    {
        'name': 'Sunset Lounge',
        'type': 'bar',
        'city': 'Birmingham',
        'timezone': 'Europe/London'
    },
    {
        'name': 'Garden Terrace',
        'type': 'restaurant',
        'city': 'Liverpool',
        'timezone': 'Europe/London'
    },
    {
        'name': 'The Craft House',
        'type': 'bar',
        'city': 'Edinburgh',
        'timezone': 'Europe/London'
    },
    {
        'name': 'Harbour View',
        'type': 'restaurant',
        'city': 'Brighton',
        'timezone': 'Europe/London'
    },
    {
        'name': 'The Local Tavern',
        'type': 'pub',
        'city': 'Oxford',
        'timezone': 'Europe/London'
    }
]

# Price ranges by category (GBP)
PRICE_RANGES = {
    'Beer': (3.50, 7.00),
    'Wine': (5.00, 12.00),
    'Spirits': (4.00, 15.00),
    'Cocktails': (8.00, 16.00),
    'Soft Drinks': (2.00, 4.50),
    'Appetizers': (5.00, 12.00),
    'Main Course': (12.00, 28.00),
    'Desserts': (5.00, 9.00),
    'Sides': (3.00, 7.00),
    'Hot Beverages': (2.50, 5.00)
}

# Output paths
OUTPUT_DIR = 'data/raw'
CSV_OUTPUT = f'{OUTPUT_DIR}/epos_transactions.csv'
PARQUET_OUTPUT = f'{OUTPUT_DIR}/epos_transactions.parquet'