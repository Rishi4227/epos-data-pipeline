"""
Database configuration for EPOS system
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Database connection settings
DATABASE_CONFIG = {
    'postgresql': {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'epos_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres')
    },
    'sqlite': {
        'database': 'data/epos.db'
    }
}

# SQLAlchemy connection strings
def get_connection_string(db_type='sqlite'):
    """Get database connection string"""
    if db_type == 'postgresql':
        config = DATABASE_CONFIG['postgresql']
        return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    elif db_type == 'sqlite':
        return f"sqlite:///{DATABASE_CONFIG['sqlite']['database']}"
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

# Default database type
DEFAULT_DB_TYPE = os.getenv('DB_TYPE', 'sqlite')