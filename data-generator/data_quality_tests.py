"""
Data quality tests for EPOS transactions
"""

import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.data_config import OUTPUT_DIR

class DataQualityTests:
    """Automated data quality checks"""
    
    def __init__(self):
        self.transactions = pd.read_parquet(f'{OUTPUT_DIR}/epos_transactions.parquet')
        self.locations = pd.read_csv(f'{OUTPUT_DIR}/locations.csv')
        self.products = pd.read_csv(f'{OUTPUT_DIR}/products.csv')
        self.employees = pd.read_csv(f'{OUTPUT_DIR}/employees.csv')
        self.tests_passed = 0
        self.tests_failed = 0
    
    def test_no_negative_amounts(self):
        """Test: No negative transaction amounts"""
        test_name = "No negative amounts"
        failed = self.transactions[self.transactions['total_amount'] < 0]
        if len(failed) == 0:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ FAIL: {test_name} - Found {len(failed)} negative amounts")
            self.tests_failed += 1
    
    def test_valid_timestamps(self):
        """Test: All timestamps are within business hours"""
        test_name = "Valid business hours"
        df = self.transactions.copy()
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        invalid = df[(df['hour'] < 10) | (df['hour'] > 23)]
        if len(invalid) == 0:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ FAIL: {test_name} - Found {len(invalid)} outside hours")
            self.tests_failed += 1
    
    def test_referential_integrity(self):
        """Test: All foreign keys exist"""
        test_name = "Referential integrity"
        
        # Check location_id
        invalid_locations = ~self.transactions['location_id'].isin(
            self.locations['location_id']
        )
        
        # Check employee_id
        invalid_employees = ~self.transactions['employee_id'].isin(
            self.employees['employee_id']
        )
        
        # Check product_id
        invalid_products = ~self.transactions['product_id'].isin(
            self.products['product_id']
        )
        
        total_invalid = (invalid_locations.sum() + 
                        invalid_employees.sum() + 
                        invalid_products.sum())
        
        if total_invalid == 0:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ FAIL: {test_name} - Found {total_invalid} invalid references")
            self.tests_failed += 1
    
    def test_transaction_math(self):
        """Test: Transaction amounts calculated correctly"""
        test_name = "Transaction math accuracy"
        
        df = self.transactions.copy()
        # Calculate expected total
        df['calculated_total'] = (df['subtotal'] + df['tax_total'] - 
                                 df['discount_total'] + df['tip_amount']).round(2)
        
        # Allow for small rounding differences
        df['difference'] = abs(df['total_amount'] - df['calculated_total'])
        invalid = df[df['difference'] > 0.01]
        
        if len(invalid) == 0:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ FAIL: {test_name} - Found {len(invalid)} calculation errors")
            self.tests_failed += 1
    
    def test_unique_ids(self):
        """Test: All IDs are unique"""
        test_name = "Unique transaction IDs"
        
        duplicates = self.transactions['transaction_id'].duplicated().sum()
        
        if duplicates == 0:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ FAIL: {test_name} - Found {duplicates} duplicate IDs")
            self.tests_failed += 1
    
    def test_status_payment_consistency(self):
        """Test: Payment status matches transaction status"""
        test_name = "Status consistency"
        
        inconsistent = self.transactions[
            ((self.transactions['transaction_status'] == 'completed') & 
             (self.transactions['payment_status'] != 'captured')) |
            ((self.transactions['transaction_status'] == 'refunded') & 
             (self.transactions['payment_status'] != 'refunded')) |
            ((self.transactions['transaction_status'] == 'error') & 
             (self.transactions['payment_status'] != 'failed'))
        ]
        
        if len(inconsistent) == 0:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ FAIL: {test_name} - Found {len(inconsistent)} inconsistencies")
            self.tests_failed += 1
    
    def test_date_range(self):
        """Test: All dates within expected range"""
        test_name = "Valid date range"
        
        min_date = pd.to_datetime('2024-01-01').date()
        max_date = pd.to_datetime('2024-12-31').date()
        
        invalid = self.transactions[
            (self.transactions['transaction_date'] < min_date) |
            (self.transactions['transaction_date'] > max_date)
        ]
        
        if len(invalid) == 0:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ FAIL: {test_name} - Found {len(invalid)} out of range")
            self.tests_failed += 1
    
    def run_all_tests(self):
        """Run all quality tests"""
        print("\n" + "="*60)
        print("DATA QUALITY TEST SUITE")
        print("="*60 + "\n")
        
        self.test_unique_ids()
        self.test_no_negative_amounts()
        self.test_valid_timestamps()
        self.test_referential_integrity()
        self.test_transaction_math()
        self.test_status_payment_consistency()
        self.test_date_range()
        
        print("\n" + "="*60)
        print(f"RESULTS: {self.tests_passed} passed, {self.tests_failed} failed")
        print("="*60 + "\n")
        
        return self.tests_failed == 0

if __name__ == "__main__":
    tester = DataQualityTests()
    all_passed = tester.run_all_tests()
    
    if all_passed:
        print("✅ All quality checks passed!")
        sys.exit(0)
    else:
        print("❌ Some quality checks failed!")
        sys.exit(1)