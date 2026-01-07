"""
Create database schema and tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config.database_config import get_connection_string, DEFAULT_DB_TYPE
from sql.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_database_schema(db_type=DEFAULT_DB_TYPE, drop_existing=False):
    """
    Create database schema
    
    Args:
        db_type: Database type ('sqlite' or 'postgresql')
        drop_existing: If True, drop existing tables first
    """
    try:
        # Get connection string
        connection_string = get_connection_string(db_type)
        logger.info(f"Connecting to database: {db_type}")
        
        # Create engine
        engine = create_engine(connection_string, echo=False)
        
        # Drop existing tables if requested
        if drop_existing:
            logger.warning("Dropping existing tables...")
            Base.metadata.drop_all(engine)
            logger.info("Existing tables dropped")
        
        # Create all tables
        logger.info("Creating database schema...")
        Base.metadata.create_all(engine)
        logger.info("✅ Database schema created successfully!")
        
        # Print created tables
        logger.info("\nCreated tables:")
        for table_name in Base.metadata.tables.keys():
            logger.info(f"  - {table_name}")
        
        return engine
        
    except Exception as e:
        logger.error(f"Error creating schema: {str(e)}")
        raise


def verify_schema(engine):
    """Verify that all tables were created"""
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    logger.info("\n" + "="*60)
    logger.info("SCHEMA VERIFICATION")
    logger.info("="*60)
    
    expected_tables = [
        'organizations', 'locations', 'employees', 
        'products', 'transactions', 'transaction_items'
    ]
    
    for table in expected_tables:
        if table in tables:
            columns = inspector.get_columns(table)
            indexes = inspector.get_indexes(table)
            logger.info(f"\n✅ Table: {table}")
            logger.info(f"   Columns: {len(columns)}")
            logger.info(f"   Indexes: {len(indexes)}")
        else:
            logger.error(f"\n❌ Table missing: {table}")
    
    logger.info("\n" + "="*60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create EPOS database schema')
    parser.add_argument('--db-type', default=DEFAULT_DB_TYPE, 
                       choices=['sqlite', 'postgresql'],
                       help='Database type')
    parser.add_argument('--drop', action='store_true',
                       help='Drop existing tables before creating')
    
    args = parser.parse_args()
    
    engine = create_database_schema(args.db_type, args.drop)
    verify_schema(engine)