# EPOS Data Pipeline

A comprehensive, production-ready EPOS (Electronic Point of Sale) analytics system that generates realistic transaction data, stores it in a database, and provides real-time business intelligence through an interactive web dashboard.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Status](https://img.shields.io/badge/status-production--ready-green.svg)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Use Cases](#use-cases)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Dashboard Features](#dashboard-features)
- [Configuration](#configuration)
- [Sample Queries](#sample-queries)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## Overview

This system provides an end-to-end solution for EPOS data analytics, from data generation to visualization. It models realistic multi-location restaurant and bar operations with over 100,000 transactions.

### What This System Does

- Generates 100,000+ realistic POS transactions
- Models multi-location restaurant/bar operations across 8 locations
- Stores data in SQLite/PostgreSQL with proper relational schema
- Provides SQL-based analytics and reporting capabilities
- Delivers interactive Streamlit dashboard for visualization
- Supports comprehensive data quality testing and validation

### Key Metrics

| Metric | Value |
|--------|-------|
| Total Transactions | 100,000 |
| Date Range | Jan 1, 2024 - Dec 31, 2024 |
| Locations | 8 (Restaurants, Bars, Pubs) |
| Products | 150 (10 categories) |
| Employees | 25 |
| Total Revenue | ~£3.09M |
| Transaction Success Rate | 92% |
| Refund Rate | 5% |

## Features

- **Realistic Data Generation**: Uses Faker library to create authentic transaction patterns
- **Robust Database Layer**: SQLAlchemy ORM with support for SQLite and PostgreSQL
- **ETL Pipeline**: Complete extract, transform, load workflow
- **Interactive Dashboard**: 8 comprehensive report views using Streamlit and Plotly
- **Data Quality Assurance**: Automated testing suite for validation
- **Multiple Export Formats**: CSV and Parquet support
- **SQL Analytics**: Pre-built queries for common business intelligence tasks

## Use Cases

- **Business Intelligence**: Real-time sales analytics and KPI tracking
- **Data Engineering Practice**: End-to-end ETL pipeline implementation
- **ML/AI Training**: Realistic dataset for predictive modeling
- **Academic Research**: Study of retail transaction patterns
- **Portfolio Project**: Demonstrate full-stack data engineering skills

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 500MB free disk space

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd epos-data-pipeline
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate (Mac/Linux)
   source venv/bin/activate
   
   # Activate (Windows)
   .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Generate Data

```bash
# Generate 100,000 transactions
python data-generator/generate_epos_data.py

# Verify data quality
python data-generator/verify_data.py

# Run quality tests
python data-generator/data_quality_tests.py
```

**Expected Output:**
- `data/raw/epos_transactions.csv` (13.6 MB)
- `data/raw/epos_transactions.parquet` (2.8 MB)
- `data/raw/locations.csv`
- `data/raw/products.csv`
- `data/raw/employees.csv`

### Setup Database

```bash
# Create database schema
python sql/create_schema.py --drop

# Load data into database
python sql/load_data.py
```

**Expected Output:**
- `data/epos.db` (SQLite database with all tables)

### Run Analytics

```bash
# Run all SQL queries
python sql/queries.py

# Generate specific reports
python sql/analytics_cli.py daily
python sql/analytics_cli.py location
python sql/analytics_cli.py employee
```

### Launch Dashboard

```bash
# Start Streamlit dashboard
streamlit run dashboard/epos_dashboard.py
```

Dashboard will open at `http://localhost:8501`

## Project Structure

```
epos-data-pipeline/
│
├── config/                          # Configuration files
│   ├── __init__.py
│   ├── data_config.py              # Data generation parameters
│   └── database_config.py          # Database connection settings
│
├── data/                            # Data storage
│   ├── raw/                        # Generated raw data
│   │   ├── epos_transactions.csv
│   │   ├── epos_transactions.parquet
│   │   ├── locations.csv
│   │   ├── products.csv
│   │   └── employees.csv
│   ├── processed/                  # Processed/exported data
│   └── epos.db                     # SQLite database file
│
├── data-generator/                  # Data generation scripts
│   ├── generate_epos_data.py       # Main data generator
│   ├── verify_data.py              # Data verification script
│   ├── data_quality_tests.py       # Automated quality checks
│   ├── run.sh                      # Launch script (Mac/Linux)
│   └── run.bat                     # Launch script (Windows)
│
├── sql/                            # Database layer
│   ├── models.py                   # SQLAlchemy ORM models
│   ├── create_schema.py            # Schema creation script
│   ├── load_data.py                # ETL pipeline script
│   ├── queries.py                  # Pre-built SQL analytics queries
│   └── analytics_cli.py            # Command-line analytics tool
│
├── dashboard/                       # Web dashboard
│   ├── epos_dashboard.py           # Streamlit dashboard app
│   ├── run_dashboard.sh            # Launch script (Mac/Linux)
│   └── run_dashboard.bat           # Launch script (Windows)
│
├── notebooks/                       # Jupyter notebooks (optional)
│   └── epos_analytics.ipynb        # Interactive analysis notebook
│
├── tests/                          # Unit tests
├── logs/                           # Application logs
├── .env                            # Environment variables
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Database Schema

### Entity Relationship Diagram

```
organizations (1) ──────┐
                        │
                        ├──> (M) locations (1) ──────┐
                        │                            │
                        │                            ├──> (M) transactions
                        │                            │
                        └──> (M) employees ──────────┘
                        
                        └──> (M) products ───────────> (M) transaction_items
```

### Tables

- **organizations** - Business/company information
- **locations** - Physical store locations (8 locations)
- **employees** - Staff members (25 employees)
- **products** - Product catalog (150 products across 10 categories)
- **transactions** - Main transaction table (100,000 records)
- **transaction_items** - Line items within transactions

### Product Categories

- Beer
- Wine
- Spirits
- Cocktails
- Soft Drinks
- Appetizers
- Main Course
- Desserts
- Sides
- Hot Beverages

### Location Types

- Restaurants (3 locations)
- Bars (3 locations)
- Pubs (2 locations)

### Payment Methods

- Credit Card (45%)
- Debit Card (30%)
- Cash (15%)
- Mobile Payment (8%)
- Gift Card (2%)

## Dashboard Features

The Streamlit dashboard provides 8 comprehensive report views:

### 1. Overview Dashboard
- Key performance indicators (KPIs)
- Revenue trends (90-day rolling average)
- Location performance comparison
- Product category distribution
- Hourly transaction patterns

### 2. Daily Sales Analysis
- Daily revenue trends with moving averages
- Transaction volume analysis
- Refund tracking
- Best performing days identification

### 3. Location Performance
- Top 3 locations (podium view)
- Revenue comparison by location type
- Performance matrix (volume vs. value)
- Detailed location metrics

### 4. Product Performance
- Category revenue breakdown
- Top 20 best-selling products
- Product distribution analysis
- Category-wise insights and recommendations

### 5. Employee Metrics
- Top performers by revenue and volume
- Transaction volume analysis
- Average transaction value comparison
- Role-based performance evaluation

### 6. Payment Method Analysis
- Payment method distribution
- Volume vs. revenue comparison
- Digital payment adoption rate
- Method-wise detailed metrics

### 7. Peak Hours Analysis
- Hourly transaction volume heatmap
- Peak revenue hours identification
- Average transaction value by hour
- Operating hours optimization insights

### 8. Refund Analysis
- Total refunds and amounts
- Refund rate tracking over time
- Location-wise refund breakdown
- Action items and improvement suggestions

## Configuration

### Database Configuration

Edit `config/database_config.py`:

```python
# Switch between SQLite and PostgreSQL
DEFAULT_DB_TYPE = 'sqlite'  # or 'postgresql'

# PostgreSQL settings (if using)
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'epos_db'
DB_USER = 'postgres'
DB_PASSWORD = 'your_password'
```

### Data Generation Configuration

Edit `config/data_config.py`:

```python
NUM_TRANSACTIONS = 100000  # Number of transactions to generate
NUM_LOCATIONS = 8          # Number of locations
NUM_PRODUCTS = 150         # Number of products
NUM_EMPLOYEES = 25         # Number of employees

START_DATE = "2024-01-01"
END_DATE = "2024-12-31"

BUSINESS_HOURS = {
    'open': 10,   # 10 AM
    'close': 23   # 11 PM
}
```

## Sample Queries

### Daily Revenue

```sql
SELECT 
    transaction_date,
    COUNT(*) as transaction_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_transaction
FROM transactions
WHERE transaction_status = 'completed'
GROUP BY transaction_date
ORDER BY transaction_date;
```

### Top Locations

```sql
SELECT 
    l.location_name,
    l.city,
    COUNT(t.transaction_id) as sales_count,
    SUM(t.total_amount) as revenue
FROM locations l
JOIN transactions t ON l.location_id = t.location_id
WHERE t.transaction_status = 'completed'
GROUP BY l.location_id
ORDER BY revenue DESC;
```

### Hourly Transaction Patterns

```sql
SELECT 
    CAST(strftime('%H', timestamp) AS INTEGER) as hour,
    COUNT(*) as transactions,
    SUM(total_amount) as revenue
FROM transactions
WHERE transaction_status = 'completed'
GROUP BY hour
ORDER BY hour;
```

### Top Products by Category

```sql
SELECT 
    p.category,
    p.product_name,
    SUM(ti.quantity) as units_sold,
    SUM(ti.line_total) as revenue
FROM products p
JOIN transaction_items ti ON p.product_id = ti.product_id
JOIN transactions t ON ti.transaction_id = t.transaction_id
WHERE t.transaction_status = 'completed'
GROUP BY p.category, p.product_name
ORDER BY revenue DESC
LIMIT 20;
```

## Testing

### Run Data Quality Tests

```bash
python data-generator/data_quality_tests.py
```

### Test Coverage

- No negative amounts validation
- Valid business hours verification
- Referential integrity checks
- Transaction math accuracy
- Unique transaction ID validation
- Status consistency verification
- Valid date range confirmation

## Deployment

### Option 1: Streamlit Cloud (Free)

1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy `dashboard/epos_dashboard.py`

### Option 2: Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "dashboard/epos_dashboard.py"]
```

Build and run:

```bash
docker build -t epos-dashboard .
docker run -p 8501:8501 epos-dashboard
```

### Option 3: Cloud VM (AWS/GCP/Azure)

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip

# Setup application
git clone <your-repo>
cd epos-data-pipeline
pip3 install -r requirements.txt

# Run dashboard
streamlit run dashboard/epos_dashboard.py --server.port 80
```

## Troubleshooting

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Mac/Linux
.\venv\Scripts\activate   # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Locked

```bash
# Clear database and reload
python sql/create_schema.py --drop
python sql/load_data.py
```

### Dashboard Not Loading

```bash
# Clear Streamlit cache
streamlit cache clear
streamlit run dashboard/epos_dashboard.py
```

### Data Generation Fails

```bash
# Check logs
cat logs/data_generation.log

# Regenerate data
python data-generator/generate_epos_data.py
```

## Future Enhancements

### Planned Features

- **REST API (FastAPI)**
  - `/api/transactions` - Get transactions
  - `/api/analytics/daily` - Daily metrics
  - `/api/locations/{id}` - Location details

- **Authentication & Authorization**
  - User login system
  - Role-based access control
  - Multi-tenant support

- **Real-Time Processing**
  - WebSocket connections
  - Live transaction streaming
  - Push notifications

- **Machine Learning**
  - Sales forecasting models
  - Anomaly detection
  - Customer segmentation
  - Churn prediction

- **Advanced Analytics**
  - Cohort analysis
  - RFM segmentation
  - Market basket analysis
  - A/B testing framework

- **Export Features**
  - PDF report generation
  - Excel export with formatting
  - Email scheduling
  - Slack/Teams integration

## Dependencies

### Core Libraries

```
# Data Generation & Processing
faker==22.0.0
pandas==2.1.4
numpy==1.26.3
pyarrow==14.0.2

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# Visualization
streamlit==1.29.0
plotly==5.18.0
matplotlib==3.8.2
seaborn==0.13.1

# Utilities
python-dateutil==2.8.2
python-dotenv==1.0.0
tqdm==4.66.1
pydantic==2.5.3

# Development
pytest==7.4.3
black==23.12.1
flake8==7.0.0
jupyter==1.0.0
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

```bash
# Format code
black .

# Lint code
flake8 .

# Run tests
pytest
```

## Learning Resources

- **Python**: [docs.python.org](https://docs.python.org)
- **Pandas**: [pandas.pydata.org](https://pandas.pydata.org)
- **SQLAlchemy**: [docs.sqlalchemy.org](https://docs.sqlalchemy.org)
- **Streamlit**: [docs.streamlit.io](https://docs.streamlit.io)
- **Plotly**: [plotly.com/python](https://plotly.com/python)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Faker](https://faker.readthedocs.io/) - Realistic data generation
- [Streamlit](https://streamlit.io/) - Rapid dashboard development
- [Plotly](https://plotly.com/) - Interactive visualizations
- [SQLAlchemy](https://www.sqlalchemy.org/) - Robust ORM framework

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact: your-email@example.com

## Project Status

### Completion Checklist

- [x] Data generation (100K transactions)
- [x] Database schema design
- [x] ETL pipeline implementation
- [x] SQL analytics queries
- [x] Interactive dashboard (8 views)
- [x] Data quality testing
- [x] Documentation
- [ ] Unit tests
- [ ] REST API
- [ ] Authentication
- [ ] Cloud deployment
- [ ] Machine learning models

---

**Built for Data Engineering Excellence**

For questions or support, please open an issue or contact the maintainers.