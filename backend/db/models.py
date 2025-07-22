# backend/db/models.py
from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func # Import func for default date if needed
import datetime # Import datetime module

Base = declarative_base()

class Receipt(Base):
    __tablename__ = "receipts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False) # Added to store original file type
    saved_path = Column(String, nullable=False)
    vendor = Column(String)
    # Use Date type for date fields for proper database handling
    # Consider storing as String if parsing is inconsistent or if you prefer to handle date parsing/validation in application logic
    transaction_date = Column(Date)
    amount = Column(Float)
    category = Column(String)
    currency = Column(String)
    # Add a timestamp for when the record was created
    created_at = Column(Date, default=datetime.date.today) # Or use DateTime and func.now() for current timestamp


    def __repr__(self):
        return f"<Receipt(id={self.id}, vendor='{self.vendor}', amount={self.amount})>"

    # Optional: Method to convert to dictionary for API responses
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "content_type": self.content_type,
            "saved_path": self.saved_path,
            "vendor": self.vendor,
            "transaction_date": self.transaction_date.isoformat() if self.transaction_date else None, # Format date as string
            "amount": self.amount,
            "category": self.category,
            "currency": self.currency,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }