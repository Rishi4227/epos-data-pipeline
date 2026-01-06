"""
EPOS Transaction Data Generator
Generates realistic point-of-sale transaction data for multiple locations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
from tqdm import tqdm
import logging
from pathlib import Path

from config.data_config import *

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EPOSDataGenerator:
    """Generate realistic EPOS transaction data"""
    
    def __init__(self):
        self.faker = Faker('en_GB')
        Faker.seed(42)
        random.seed(42)
        np.random.seed(42)
        
        self.locations = self._generate_locations()
        self.products = self._generate_products()
        self.employees = self._generate_employees()
        
        logger.info(f"Initialized generator with {len(self.locations)} locations, "
                   f"{len(self.products)} products, {len(self.employees)} employees")
    
    def _generate_locations(self):
        """Generate location master data"""
        locations = []
        for i, loc_config in enumerate(LOCATIONS):
            location = {
                'location_id': f'LOC-{i+1:03d}',
                'location_name': loc_config['name'],
                'location_type': loc_config['type'],
                'city': loc_config['city'],
                'timezone': loc_config['timezone'],
                'address': self.faker.street_address(),
                'postal_code': self.faker.postcode()
            }
            locations.append(location)
        return pd.DataFrame(locations)
    
    def _generate_products(self):
        """Generate product catalog"""
        products = []
        product_id = 1
        
        for category in PRODUCT_CATEGORIES:
            # Generate 15 products per category
            num_products_in_category = NUM_PRODUCTS // len(PRODUCT_CATEGORIES)
            
            for _ in range(num_products_in_category):
                min_price, max_price = PRICE_RANGES[category]
                
                product = {
                    'product_id': f'PRD-{product_id:05d}',
                    'product_name': self._generate_product_name(category),
                    'product_category': category,
                    'base_price': round(random.uniform(min_price, max_price), 2),
                    'cost_price': round(random.uniform(min_price * 0.3, min_price * 0.6), 2),
                    'sku': f'SKU-{product_id:05d}',
                    'is_taxable': True,
                    'tax_rate': 0.20  # 20% VAT
                }
                products.append(product)
                product_id += 1
        
        return pd.DataFrame(products)
    
    def _generate_product_name(self, category):
        """Generate realistic product names by category"""
        names = {
            'Beer': [f"{self.faker.company()} {beer}" for beer in 
                    ['Lager', 'IPA', 'Pale Ale', 'Stout', 'Pilsner']],
            'Wine': [f"{self.faker.last_name()} {wine}" for wine in 
                    ['Chardonnay', 'Merlot', 'Pinot Noir', 'Sauvignon Blanc', 'Rosé']],
            'Spirits': ['Vodka', 'Gin', 'Rum', 'Whisky', 'Tequila', 'Bourbon'],
            'Cocktails': ['Mojito', 'Margarita', 'Old Fashioned', 'Martini', 
                         'Cosmopolitan', 'Manhattan'],
            'Soft Drinks': ['Cola', 'Lemonade', 'Orange Juice', 'Tonic Water', 
                           'Ginger Ale'],
            'Appetizers': ['Chicken Wings', 'Nachos', 'Garlic Bread', 'Calamari', 
                          'Mozzarella Sticks'],
            'Main Course': ['Burger', 'Steak', 'Fish & Chips', 'Pasta', 'Pizza', 
                           'Salad Bowl'],
            'Desserts': ['Chocolate Cake', 'Ice Cream', 'Cheesecake', 'Brownie', 
                        'Apple Pie'],
            'Sides': ['Fries', 'Coleslaw', 'Onion Rings', 'Side Salad', 'Vegetables'],
            'Hot Beverages': ['Espresso', 'Cappuccino', 'Latte', 'Tea', 'Hot Chocolate']
        }
        return random.choice(names.get(category, [category]))
    
    def _generate_employees(self):
        """Generate employee master data"""
        employees = []
        for i in range(NUM_EMPLOYEES):
            employee = {
                'employee_id': f'EMP-{i+1:04d}',
                'first_name': self.faker.first_name(),
                'last_name': self.faker.last_name(),
                'role': random.choice(['cashier', 'cashier', 'cashier', 'manager']),
                'location_id': random.choice(self.locations['location_id'].tolist())
            }
            employees.append(employee)
        return pd.DataFrame(employees)
    
    def _generate_timestamp(self, date):
        """Generate realistic timestamp within business hours"""
        # Peak hours: 12-14 (lunch), 18-21 (dinner/evening)
        hour_weights = [0.5] * 10 + [2] * 2 + [1] * 2 + [0.5] * 2 + [3] * 4 + [1] * 4
        
        hour = random.choices(
            range(BUSINESS_HOURS['open'], BUSINESS_HOURS['close'] + 1),
            weights=hour_weights[:len(range(BUSINESS_HOURS['open'], 
                                           BUSINESS_HOURS['close'] + 1))]
        )[0]
        
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        return datetime.combine(date, datetime.min.time()) + timedelta(
            hours=hour, minutes=minute, seconds=second
        )
    
    def _determine_transaction_status(self):
        """Determine transaction status based on distribution"""
        statuses = list(TRANSACTION_STATUS_DISTRIBUTION.keys())
        weights = list(TRANSACTION_STATUS_DISTRIBUTION.values())
        return random.choices(statuses, weights=weights)[0]
    
    def _determine_payment_method(self):
        """Determine payment method based on distribution"""
        methods = list(PAYMENT_METHOD_DISTRIBUTION.keys())
        weights = list(PAYMENT_METHOD_DISTRIBUTION.values())
        return random.choices(methods, weights=weights)[0]
    
    def generate_transactions(self):
        """Generate complete transaction dataset"""
        logger.info(f"Generating {NUM_TRANSACTIONS} transactions...")
        
        transactions = []
        start_date = datetime.strptime(START_DATE, '%Y-%m-%d').date()
        end_date = datetime.strptime(END_DATE, '%Y-%m-%d').date()
        date_range = (end_date - start_date).days
        
        for i in tqdm(range(NUM_TRANSACTIONS), desc="Generating transactions"):
            # Random date within range
            random_date = start_date + timedelta(days=random.randint(0, date_range))
            timestamp = self._generate_timestamp(random_date)
            
            # Select location, employee, and product
            location = self.locations.sample(1).iloc[0]
            employee = self.employees[
                self.employees['location_id'] == location['location_id']
            ].sample(1).iloc[0] if len(
                self.employees[self.employees['location_id'] == location['location_id']]
            ) > 0 else self.employees.sample(1).iloc[0]
            
            # Number of items (1-6 items per transaction)
            num_items = random.choices([1, 2, 3, 4, 5, 6], 
                                      weights=[30, 30, 20, 10, 7, 3])[0]
            
            # Generate items for this transaction
            selected_products = self.products.sample(num_items)
            
            subtotal = 0
            tax_total = 0
            
            for _, product in selected_products.iterrows():
                quantity = random.choices([1, 2, 3], weights=[70, 20, 10])[0]
                unit_price = product['base_price']
                item_subtotal = quantity * unit_price
                item_tax = item_subtotal * product['tax_rate'] if product['is_taxable'] else 0
                
                subtotal += item_subtotal
                tax_total += item_tax
            
            # Apply random discount (10% chance)
            discount_total = 0
            if random.random() < 0.10:
                discount_total = round(subtotal * random.uniform(0.05, 0.20), 2)
            
            # Tip (30% of transactions, mainly in restaurants)
            tip_amount = 0
            if location['location_type'] == 'restaurant' and random.random() < 0.30:
                tip_amount = round(subtotal * random.uniform(0.10, 0.20), 2)
            
            total_amount = round(subtotal + tax_total - discount_total + tip_amount, 2)
            
            # Transaction status and payment
            status = self._determine_transaction_status()
            payment_method = self._determine_payment_method()
            
            # Payment status based on transaction status
            if status == 'completed':
                payment_status = 'captured'
            elif status == 'refunded':
                payment_status = 'refunded'
            elif status == 'error':
                payment_status = 'failed'
            else:
                payment_status = 'voided'
            
            transaction = {
                'transaction_id': f'TXN-{i+1:08d}',
                'transaction_number': f'#{random.randint(100000, 999999)}',
                'timestamp': timestamp,
                'transaction_date': random_date,
                'transaction_time': timestamp.time(),
                'location_id': location['location_id'],
                'location_name': location['location_name'],
                'location_type': location['location_type'],
                'city': location['city'],
                'device_id': f'DEV-{location["location_id"]}-{random.randint(1, 3):02d}',
                'employee_id': employee['employee_id'],
                'employee_name': f"{employee['first_name']} {employee['last_name']}",
                'num_items': num_items,
                'product_id': selected_products.iloc[0]['product_id'],  # Primary product
                'product_name': selected_products.iloc[0]['product_name'],
                'product_category': selected_products.iloc[0]['product_category'],
                'quantity': num_items,
                'unit_price': selected_products.iloc[0]['base_price'],
                'subtotal': round(subtotal, 2),
                'tax_total': round(tax_total, 2),
                'discount_total': round(discount_total, 2),
                'tip_amount': round(tip_amount, 2),
                'total_amount': total_amount,
                'payment_method': payment_method,
                'payment_status': payment_status,
                'transaction_status': status,
                'card_last_four': f'{random.randint(1000, 9999)}' if 'card' in payment_method else None,
                'authorization_code': f'AUTH-{random.randint(100000, 999999)}' if payment_status == 'captured' else None
            }
            
            transactions.append(transaction)
        
        df = pd.DataFrame(transactions)
        logger.info(f"Generated {len(df)} transactions")
        return df
    
    def save_data(self, df):
        """Save data to CSV and Parquet formats"""
        # Ensure output directory exists
        Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        
        # Save to CSV
        logger.info(f"Saving to CSV: {CSV_OUTPUT}")
        df.to_csv(CSV_OUTPUT, index=False)
        
        # Save to Parquet
        logger.info(f"Saving to Parquet: {PARQUET_OUTPUT}")
        df.to_parquet(PARQUET_OUTPUT, index=False, engine='pyarrow')
        
        # Save master data
        self.locations.to_csv(f'{OUTPUT_DIR}/locations.csv', index=False)
        self.products.to_csv(f'{OUTPUT_DIR}/products.csv', index=False)
        self.employees.to_csv(f'{OUTPUT_DIR}/employees.csv', index=False)
        
        logger.info("All data saved successfully")
        
        # Print summary statistics
        self._print_summary(df)
    
    def _print_summary(self, df):
        """Print summary statistics"""
        print("\n" + "="*60)
        print("DATA GENERATION SUMMARY")
        print("="*60)
        print(f"Total Transactions: {len(df):,}")
        print(f"Date Range: {df['transaction_date'].min()} to {df['transaction_date'].max()}")
        print(f"Total Revenue: £{df[df['transaction_status']=='completed']['total_amount'].sum():,.2f}")
        print(f"\nLocations: {df['location_name'].nunique()}")
        print(f"Products: {len(self.products)}")
        print(f"Employees: {len(self.employees)}")
        print(f"\nTransaction Status Distribution:")
        print(df['transaction_status'].value_counts())
        print(f"\nPayment Method Distribution:")
        print(df['payment_method'].value_counts())
        print(f"\nTop 5 Categories by Revenue:")
        category_revenue = df[df['transaction_status']=='completed'].groupby('product_category')['total_amount'].sum().sort_values(ascending=False)
        print(category_revenue.head())
        print("="*60 + "\n")


def main():
    """Main execution function"""
    logger.info("Starting EPOS data generation...")
    
    try:
        # Initialize generator
        generator = EPOSDataGenerator()
        
        # Generate transactions
        transactions_df = generator.generate_transactions()
        
        # Save data
        generator.save_data(transactions_df)
        
        logger.info("Data generation completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during data generation: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()