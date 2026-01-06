# EPOS Data Pipeline

Real-time multimodal EPOS transaction data generation and processing system.

## Project Structure
```
epos-data-pipeline/
├── data-generator/          # Data generation scripts
├── data/
│   ├── raw/                # Generated raw data (CSV, Parquet)
│   └── processed/          # Processed/cleaned data
├── notebooks/              # Jupyter notebooks for analysis
├── sql/                    # SQL scripts and schema definitions
├── tests/                  # Unit tests
├── config/                 # Configuration files
├── logs/                   # Application logs
├── requirements.txt        # Python dependencies
└── README.md
```

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
.\venv\Scripts\activate   # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Generate data:
```bash
python data-generator/generate_epos_data.py
```

## Generated Data

- **Transactions**: ~100,000 rows
- **Locations**: Multiple bar/restaurant locations
- **Format**: CSV + Parquet
- **Features**: Sales, refunds, errors, timestamps