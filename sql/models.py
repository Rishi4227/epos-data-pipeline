"""
SQLAlchemy ORM models for EPOS database
"""

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Date, Time, 
    Boolean, Enum, ForeignKey, Text, DECIMAL, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class TransactionStatus(enum.Enum):
    """Transaction status enumeration"""
    COMPLETED = 'completed'
    REFUNDED = 'refunded'
    VOIDED = 'voided'
    ERROR = 'error'


class PaymentStatus(enum.Enum):
    """Payment status enumeration"""
    CAPTURED = 'captured'
    REFUNDED = 'refunded'
    FAILED = 'failed'
    VOIDED = 'voided'


class PaymentMethod(enum.Enum):
    """Payment method enumeration"""
    CREDIT_CARD = 'credit_card'
    DEBIT_CARD = 'debit_card'
    CASH = 'cash'
    MOBILE_PAYMENT = 'mobile_payment'
    GIFT_CARD = 'gift_card'


class Organization(Base):
    """Organization/Business entity"""
    __tablename__ = 'organizations'
    
    organization_id = Column(String(50), primary_key=True)
    business_name = Column(String(255), nullable=False)
    business_type = Column(String(100))
    tax_id = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default='active')
    
    # Relationships
    locations = relationship("Location", back_populates="organization")


class Location(Base):
    """Physical locations"""
    __tablename__ = 'locations'
    
    location_id = Column(String(50), primary_key=True)
    organization_id = Column(String(50), ForeignKey('organizations.organization_id'))
    location_name = Column(String(255), nullable=False)
    location_type = Column(String(50))
    city = Column(String(100))
    address = Column(String(255))
    postal_code = Column(String(20))
    timezone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='active')
    
    # Relationships
    organization = relationship("Organization", back_populates="locations")
    transactions = relationship("Transaction", back_populates="location")
    
    # Indexes
    __table_args__ = (
        Index('idx_location_org', 'organization_id'),
        Index('idx_location_city', 'city'),
    )


class Employee(Base):
    """Employees/Staff members"""
    __tablename__ = 'employees'
    
    employee_id = Column(String(50), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(50))
    location_id = Column(String(50), ForeignKey('locations.location_id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='active')
    
    # Relationships
    transactions = relationship("Transaction", back_populates="employee")
    
    # Indexes
    __table_args__ = (
        Index('idx_employee_location', 'location_id'),
    )


class Product(Base):
    """Product catalog"""
    __tablename__ = 'products'
    
    product_id = Column(String(50), primary_key=True)
    product_name = Column(String(255), nullable=False)
    product_category = Column(String(100))
    sku = Column(String(100), unique=True)
    base_price = Column(DECIMAL(10, 2), nullable=False)
    cost_price = Column(DECIMAL(10, 2))
    tax_rate = Column(DECIMAL(5, 4))
    is_taxable = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='active')
    
    # Relationships
    transaction_items = relationship("TransactionItem", back_populates="product")
    
    # Indexes
    __table_args__ = (
        Index('idx_product_category', 'product_category'),
        Index('idx_product_sku', 'sku'),
    )


class Transaction(Base):
    """Main transaction table"""
    __tablename__ = 'transactions'
    
    transaction_id = Column(String(50), primary_key=True)
    transaction_number = Column(String(50), unique=True, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    transaction_date = Column(Date, nullable=False)
    transaction_time = Column(Time, nullable=False)
    
    # Foreign keys
    location_id = Column(String(50), ForeignKey('locations.location_id'), nullable=False)
    employee_id = Column(String(50), ForeignKey('employees.employee_id'), nullable=False)
    device_id = Column(String(50))
    
    # Amounts
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    tax_total = Column(DECIMAL(10, 2), nullable=False)
    discount_total = Column(DECIMAL(10, 2), default=0.00)
    tip_amount = Column(DECIMAL(10, 2), default=0.00)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    
    # Status
    transaction_status = Column(Enum(TransactionStatus), nullable=False)
    payment_status = Column(Enum(PaymentStatus), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    
    # Payment details
    card_last_four = Column(String(4))
    authorization_code = Column(String(50))
    
    # Metadata
    num_items = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    location = relationship("Location", back_populates="transactions")
    employee = relationship("Employee", back_populates="transactions")
    items = relationship("TransactionItem", back_populates="transaction")
    
    # Indexes
    __table_args__ = (
        Index('idx_transaction_date', 'transaction_date'),
        Index('idx_transaction_location', 'location_id'),
        Index('idx_transaction_status', 'transaction_status'),
        Index('idx_transaction_timestamp', 'timestamp'),
        Index('idx_transaction_location_date', 'location_id', 'transaction_date'),
    )


class TransactionItem(Base):
    """Individual items within transactions"""
    __tablename__ = 'transaction_items'
    
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(50), ForeignKey('transactions.transaction_id'), nullable=False)
    product_id = Column(String(50), ForeignKey('products.product_id'), nullable=False)
    
    quantity = Column(DECIMAL(10, 3), nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    item_subtotal = Column(DECIMAL(10, 2), nullable=False)
    discount_amount = Column(DECIMAL(10, 2), default=0.00)
    tax_amount = Column(DECIMAL(10, 2), nullable=False)
    item_total = Column(DECIMAL(10, 2), nullable=False)
    
    line_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product", back_populates="transaction_items")
    
    # Indexes
    __table_args__ = (
        Index('idx_item_transaction', 'transaction_id'),
        Index('idx_item_product', 'product_id'),
    )