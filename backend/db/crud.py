# backend/db/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date, asc, desc
from backend.db.models import Receipt
from datetime import date as DateType, datetime
from typing import Dict, Any, List, Optional, Tuple
import re # Import regex module

def create_receipt(db: Session,
                   filename: str,
                   content_type: str,
                   saved_path: str,
                   parsed_data: Dict[str, Any]) -> Receipt:
    """
    Creates a new receipt record in the database.
    """
    vendor = parsed_data.get("vendor")
    amount = parsed_data.get("amount")
    category = parsed_data.get("category")
    currency = parsed_data.get("currency")

    transaction_date_str = parsed_data.get("date") # Assuming 'date' is the key from parse_receipt_text
    transaction_date: Optional[DateType] = None
    if transaction_date_str:
        # Attempt to parse common date formats for storage as DateType
        # This is a basic example; more robust parsing would go here.
        try:
            # Example: Try YYYY-MM-DD or MM/DD/YYYY
            if '-' in transaction_date_str:
                transaction_date = datetime.strptime(transaction_date_str, '%Y-%m-%d').date()
            elif '/' in transaction_date_str:
                transaction_date = datetime.strptime(transaction_date_str, '%m/%d/%Y').date()
            # Add more formats as needed based on OCR output patterns
        except ValueError:
            print(f"Warning: Could not parse date '{transaction_date_str}'. Storing as None.")
            transaction_date = None

    db_receipt = Receipt(
        filename=filename,
        content_type=content_type,
        saved_path=saved_path,
        vendor=vendor,
        transaction_date=transaction_date,
        amount=amount,
        category=category,
        currency=currency
    )
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)
    return db_receipt

def get_receipts(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of receipt records from the database.
    """
    return db.query(Receipt).offset(skip).limit(limit).all()

def get_receipt(db: Session, receipt_id: int):
    """
    Retrieves a single receipt record by its ID.
    """
    return db.query(Receipt).filter(Receipt.id == receipt_id).first()

def update_receipt(db: Session, receipt_id: int, update_data: Dict[str, Any]):
    """
    Updates an existing receipt record.
    """
    db_receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if db_receipt:
        for key, value in update_data.items():
            if key == "transaction_date" and isinstance(value, str):
                try:
                    # Attempt to parse date string to DateType for updates
                    db_receipt.transaction_date = DateType.fromisoformat(value)
                except ValueError:
                    print(f"Warning: Could not parse update date '{value}'. Date not updated.")
            else:
                setattr(db_receipt, key, value)
        db.commit()
        db.refresh(db_receipt)
        return db_receipt
    return None

def delete_receipt(db: Session, receipt_id: int):
    """
    Deletes a receipt record from the database.
    """
    db_receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if db_receipt:
        db.delete(db_receipt)
        db.commit()
        return True
    return False

# --- Algorithmic Logic Additions ---

def search_receipts(
    db: Session,
    keyword: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    start_date: Optional[DateType] = None,
    end_date: Optional[DateType] = None,
    vendor_pattern: Optional[str] = None, # For regex/wildcard search on vendor
    skip: int = 0,
    limit: int = 100
) -> List[Receipt]:
    """
    Searches receipts based on various criteria.
    - Keyword search across filename, vendor, category.
    - Range-based queries for amount and date.
    - Pattern matching (regex) on vendor names.
    """
    query = db.query(Receipt)

    if keyword:
        # Case-insensitive keyword search across relevant string fields
        search_keyword = f"%{keyword.lower()}%"
        query = query.filter(
            (func.lower(Receipt.filename).like(search_keyword)) |
            (func.lower(Receipt.vendor).like(search_keyword)) |
            (func.lower(Receipt.category).like(search_keyword))
        )

    if min_amount is not None:
        query = query.filter(Receipt.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Receipt.amount <= max_amount)

    if start_date:
        query = query.filter(Receipt.transaction_date >= start_date)
    if end_date:
        query = query.filter(Receipt.transaction_date <= end_date)

    if vendor_pattern:
        # Use SQLite's REGEXP operator (requires connection to support it, or rely on Python regex)
        # For SQLite, it's often easier to fetch and filter in Python for complex regex if not enabled.
        # However, for simple LIKE patterns, we can use it. For full regex, SQLAlchemy's match() isn't standard.
        # Let's use a simple LIKE for wildcards for better DB performance/compatibility.
        # If full regex is strictly needed for SQLite without extension, one might fetch all and filter in Python.
        # For `vendor_pattern` like "Walmart%", use `like`. If it's a true regex, you'd need SQLite REGEXP extension.
        # For simplicity and broad compatibility, let's assume `vendor_pattern` uses SQL LIKE wildcards (%)
        query = query.filter(func.lower(Receipt.vendor).like(f"%{vendor_pattern.lower()}%"))

    return query.offset(skip).limit(limit).all()


def sort_receipts(
    db: Session,
    sort_by: str, # 'amount', 'date', 'vendor'
    sort_order: str = "asc", # 'asc' or 'desc'
    skip: int = 0,
    limit: int = 100
) -> List[Receipt]:
    """
    Sorts receipts based on a specified field and order.
    """
    query = db.query(Receipt)

    if sort_by == "amount":
        if sort_order == "desc":
            query = query.order_by(desc(Receipt.amount))
        else:
            query = query.order_by(asc(Receipt.amount))
    elif sort_by == "date":
        if sort_order == "desc":
            query = query.order_by(desc(Receipt.transaction_date))
        else:
            query = query.order_by(asc(Receipt.transaction_date))
    elif sort_by == "vendor":
        if sort_order == "desc":
            query = query.order_by(desc(Receipt.vendor))
        else:
            query = query.order_by(asc(Receipt.vendor))
    else:
        # Default sort if invalid sort_by is provided
        query = query.order_by(asc(Receipt.id))

    return query.offset(skip).limit(limit).all()

# --- Aggregation Functions ---

def get_total_spend(db: Session) -> float:
    """Computes the total sum of all receipt amounts."""
    total = db.query(func.sum(Receipt.amount)).scalar()
    return total if total is not None else 0.0

def get_spend_statistics(db: Session) -> Dict[str, Optional[float]]:
    """Computes mean, median, and mode of expenditure."""
    amounts = [r.amount for r in db.query(Receipt.amount).filter(Receipt.amount.isnot(None)).all()]
    if not amounts:
        return {"mean": None, "median": None, "mode": None}

    # Mean
    mean_val = sum(amounts) / len(amounts)

    # Median
    sorted_amounts = sorted(amounts)
    n = len(sorted_amounts)
    if n % 2 == 0:
        median_val = (sorted_amounts[n // 2 - 1] + sorted_amounts[n // 2]) / 2
    else:
        median_val = sorted_amounts[n // 2]

    # Mode (can be multiple, return the first for simplicity or a list)
    from collections import Counter
    counts = Counter(amounts)
    if counts:
        max_count = max(counts.values())
        mode_vals = [key for key, value in counts.items() if value == max_count]
        mode_val = mode_vals[0] if mode_vals else None # Return first mode if multiple
    else:
        mode_val = None

    return {"mean": mean_val, "median": median_val, "mode": mode_val}


def get_vendor_frequency(db: Session) -> Dict[str, int]:
    """Computes the frequency distribution of vendors."""
    vendor_counts = db.query(Receipt.vendor, func.count(Receipt.id))\
                      .filter(Receipt.vendor.isnot(None))\
                      .group_by(Receipt.vendor)\
                      .order_by(func.count(Receipt.id).desc())\
                      .all()
    return {vendor: count for vendor, count in vendor_counts}

def get_monthly_spend_trend(db: Session) -> List[Dict[str, Any]]:
    """
    Computes monthly spend trend.
    Returns a list of dictionaries with 'month_year' and 'total_spend'.
    """
    # SQLite often stores dates as strings in YYYY-MM-DD format.
    # We need to extract year and month from the string date.
    # For SQLite, use strftime. For other DBs, use appropriate func like EXTRACT.
    # Ensure transaction_date is not null before grouping.
    monthly_data = db.query(
        func.strftime('%Y-%m', Receipt.transaction_date).label('month_year'),
        func.sum(Receipt.amount).label('total_spend')
    )\
    .filter(Receipt.transaction_date.isnot(None), Receipt.amount.isnot(None))\
    .group_by('month_year')\
    .order_by('month_year')\
    .all()

    # Convert row objects to dictionaries
    return [{"month_year": row.month_year, "total_spend": row.total_spend} for row in monthly_data]

def get_spend_by_category(db: Session) -> List[Dict[str, Any]]:
    """
    Computes total spend per category.
    """
    category_spend = db.query(
        Receipt.category,
        func.sum(Receipt.amount).label('total_spend')
    )\
    .filter(Receipt.category.isnot(None), Receipt.amount.isnot(None))\
    .group_by(Receipt.category)\
    .order_by(func.sum(Receipt.amount).desc())\
    .all()

    return [{"category": row.category, "total_spend": row.total_spend} for row in category_spend]