"""
ETL script to load generated data into database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm
import logging

from config.database_config import get_connection_string, DEFAULT_DB_TYPE
from config.data_config import OUTPUT_DIR
from sql.models import (
    Organization, Location, Employee, Product, 
    Transaction, TransactionItem
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EPOSDataLoader:
    """Load EPOS data into database"""
    
    def __init__(self, db_type=DEFAULT_DB_TYPE):
        self.db_type = db_type
        self.engine = create_engine(get_connection_string(db_type))
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        logger.info(f"Connected to {db_type} database")
    
    def load_organizations(self):
        """Load organization data"""
        logger.info("Loading organization...")
        
        org = Organization(
            organization_id='ORG-001',
            business_name='UK Hospitality Group',
            business_type='Restaurant & Bar Chain',
            tax_id='GB123456789',
            status='active'
        )
        
        self.session.merge(org)
        self.session.commit()
        logger.info("✅ Organization loaded")
    
    def load_locations(self):
        """Load location data"""
        logger.info("Loading locations...")
        
        locations_df = pd.read_csv(f'{OUTPUT_DIR}/locations.csv')
        
        for _, row in tqdm(locations_df.iterrows(), total=len(locations_df), desc="Locations"):
            location = Location(
                location_id=row['location_id'],
                organization_id='ORG-001',
                location_name=row['location_name'],
                location_type=row['location_type'],
                city=row['city'],
                address=row['address'],
                postal_code=row['postal_code'],
                timezone=row['timezone'],
                status='active'
            )
            self.session.merge(location)
        
        self.session.commit()
        logger.info(f"✅ Loaded {len(locations_df)} locations")
    
    def load_employees(self):
        """Load employee data"""
        logger.info("Loading employees...")
        
        employees_df = pd.read_csv(f'{OUTPUT_DIR}/employees.csv')
        
        for _, row in tqdm(employees_df.iterrows(), total=len(employees_df), desc="Employees"):
            employee = Employee(
                employee_id=row['employee_id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                role=row['role'],
                location_id=row['location_id'],
                status='active'
            )
            self.session.merge(employee)
        
        self.session.commit()
        logger.info(f"✅ Loaded {len(employees_df)} employees")
    
    def load_products(self):
        """Load product catalog"""
        logger.info("Loading products...")
        
        products_df = pd.read_csv(f'{OUTPUT_DIR}/products.csv')
        
        for _, row in tqdm(products_df.iterrows(), total=len(products_df), desc="Products"):
            product = Product(
                product_id=row['product_id'],
                product_name=row['product_name'],
                product_category=row['product_category'],
                sku=row['sku'],
                base_price=float(row['base_price']),
                cost_price=float(row['cost_price']),
                tax_rate=float(row['tax_rate']),
                is_taxable=bool(row['is_taxable']),
                status='active'
            )
            self.session.merge(product)
        
        self.session.commit()
        logger.info(f"✅ Loaded {len(products_df)} products")
    
    def load_transactions(self, batch_size=1000):
        """Load transaction data in batches"""
        logger.info("Loading transactions...")
        
        # Clear existing transactions first
        self.session.execute(text("DELETE FROM transactions"))
        self.session.commit()
        logger.info("Cleared existing transactions")
        
        # Read parquet for better performance
        transactions_df = pd.read_parquet(f'{OUTPUT_DIR}/epos_transactions.parquet')
        
        # Check for duplicates and remove them
        initial_count = len(transactions_df)
        transactions_df = transactions_df.drop_duplicates(subset=['transaction_number'], keep='first')
        final_count = len(transactions_df)
        
        if initial_count != final_count:
            logger.warning(f"Removed {initial_count - final_count} duplicate transaction numbers")
        
        logger.info(f"Found {final_count:,} unique transactions to load")
        
        # Process in batches
        for start_idx in tqdm(range(0, final_count, batch_size), desc="Transaction batches"):
            end_idx = min(start_idx + batch_size, final_count)
            batch_df = transactions_df.iloc[start_idx:end_idx]
            
            for _, row in batch_df.iterrows():
                # Handle transaction_time - it's already a time object from parquet
                if isinstance(row['transaction_time'], str):
                    trans_time = pd.to_datetime(row['transaction_time']).time()
                else:
                    trans_time = row['transaction_time']
                
                transaction = Transaction(
                    transaction_id=row['transaction_id'],
                    transaction_number=row['transaction_number'],
                    timestamp=pd.to_datetime(row['timestamp']),
                    transaction_date=pd.to_datetime(row['transaction_date']).date(),
                    transaction_time=trans_time,
                    location_id=row['location_id'],
                    employee_id=row['employee_id'],
                    device_id=row['device_id'],
                    subtotal=float(row['subtotal']),
                    tax_total=float(row['tax_total']),
                    discount_total=float(row['discount_total']),
                    tip_amount=float(row['tip_amount']),
                    total_amount=float(row['total_amount']),
                    transaction_status=row['transaction_status'],
                    payment_status=row['payment_status'],
                    payment_method=row['payment_method'],
                    card_last_four=str(row['card_last_four']) if pd.notna(row['card_last_four']) else None,
                    authorization_code=row['authorization_code'] if pd.notna(row['authorization_code']) else None,
                    num_items=int(row['num_items'])
                )
                self.session.add(transaction)
            
            # Commit batch
            self.session.commit()
        
        logger.info(f"✅ Loaded {final_count:,} transactions")
    
    def load_all_data(self):
        """Load all data in correct order"""
        try:
            logger.info("\n" + "="*60)
            logger.info("STARTING ETL PROCESS")
            logger.info("="*60 + "\n")
            
            self.load_organizations()
            self.load_locations()
            self.load_employees()
            self.load_products()
            self.load_transactions()
            
            logger.info("\n" + "="*60)
            logger.info("✅ ETL PROCESS COMPLETED SUCCESSFULLY!")
            logger.info("="*60 + "\n")
            
            self.print_summary()
            
        except Exception as e:
            logger.error(f"Error during ETL: {str(e)}", exc_info=True)
            self.session.rollback()
            raise
        finally:
            self.session.close()
    
    def print_summary(self):
        """Print database summary"""
        from sqlalchemy import func
        
        print("\n" + "="*60)
        print("DATABASE SUMMARY")
        print("="*60)
        
        org_count = self.session.query(func.count(Organization.organization_id)).scalar()
        location_count = self.session.query(func.count(Location.location_id)).scalar()
        employee_count = self.session.query(func.count(Employee.employee_id)).scalar()
        product_count = self.session.query(func.count(Product.product_id)).scalar()
        transaction_count = self.session.query(func.count(Transaction.transaction_id)).scalar()
        
        print(f"Organizations: {org_count:,}")
        print(f"Locations: {location_count:,}")
        print(f"Employees: {employee_count:,}")
        print(f"Products: {product_count:,}")
        print(f"Transactions: {transaction_count:,}")
        
        # Revenue by status
        completed_revenue = self.session.query(
            func.sum(Transaction.total_amount)
        ).filter(
            Transaction.transaction_status == 'completed'
        ).scalar() or 0
        
        print(f"\nTotal Revenue (Completed): £{completed_revenue:,.2f}")
        print("="*60 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Load EPOS data into database')
    parser.add_argument('--db-type', default=DEFAULT_DB_TYPE,
                       choices=['sqlite', 'postgresql'],
                       help='Database type')
    
    args = parser.parse_args()
    
    loader = EPOSDataLoader(args.db_type)
    loader.load_all_data()