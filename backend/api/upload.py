# backend/api/upload.py
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import os
import datetime

# Local imports
from backend.core.ocr import ocr_image, ocr_pdf, parse_receipt_text, parse_text_file
from backend.db.database import get_db
from backend.db import crud
from sqlalchemy.orm import Session
from backend.db.models import Receipt as DBReceipt

router = APIRouter()

UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Pydantic models for API request/response (keep as is)
class FileUploadResponse(BaseModel):
    filename: str
    content_type: str
    message: str
    saved_path: Optional[str] = None
    parsed_fields: Optional[Dict] = None
    db_record_id: Optional[int] = None


class ReceiptUpdate(BaseModel):
    filename: Optional[str] = None
    content_type: Optional[str] = None
    saved_path: Optional[str] = None
    vendor: Optional[str] = None
    transaction_date: Optional[datetime.date] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    currency: Optional[str] = None

    class Config:
        extra = "ignore"
        from_attributes = True


class ReceiptResponse(BaseModel):
    id: int
    filename: str
    content_type: str
    saved_path: str
    vendor: Optional[str] = None
    transaction_date: Optional[datetime.date] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    currency: Optional[str] = None
    created_at: Optional[datetime.date] = None

    class Config:
        from_attributes = True


# --- File Upload Endpoint ---
@router.post("/upload", response_model=FileUploadResponse)
async def upload_receipt(file: UploadFile = File(...), db: Session = Depends(get_db)):
    allowed_types = ["image/jpeg", "image/png", "application/pdf", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_location, "wb") as f:
            f.write(await file.read())
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    text = ""
    if file.content_type in ["image/jpeg", "image/png"]:
        text = ocr_image(file_location)
    elif file.content_type == "application/pdf":
        text = ocr_pdf(file_location)
    elif file.content_type == "text/plain":
        text = parse_text_file(file_location)

    parsed_data = parse_receipt_text(text)

    try:
        db_receipt = crud.create_receipt(
            db=db,
            filename=file.filename,
            content_type=file.content_type,
            saved_path=file_location,
            parsed_data=parsed_data
        )
    except Exception as e:
        print(f"Database error during receipt creation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save receipt to database: {e}")

    return FileUploadResponse(
        filename=file.filename,
        content_type=file.content_type,
        message="File uploaded and parsed successfully!",
        saved_path=file_location,
        parsed_fields=parsed_data,
        db_record_id=db_receipt.id
    )

# --- Algorithmic Endpoints (Order is Crucial for Path Matching) ---

# 1. Most specific static path first
@router.get("/receipts/search", response_model=List[ReceiptResponse])
def search_receipts_api(
    keyword: Optional[str] = Query(None, description="Keyword to search in filename, vendor, or category"),
    min_amount: Optional[float] = Query(None, description="Minimum amount for search"),
    max_amount: Optional[float] = Query(None, description="Maximum amount for search"),
    start_date: Optional[datetime.date] = Query(None, description="Start date (YYYY-MM-DD) for transaction date range"),
    end_date: Optional[datetime.date] = Query(None, description="End date (YYYY-MM-DD) for transaction date range"),
    vendor_pattern: Optional[str] = Query(None, description="Vendor name pattern (e.g., 'Walmart%')"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Search receipts based on various criteria like keyword, amount range, date range, or vendor pattern.
    """
    print(f"Received search parameters: keyword={keyword}, min_amount={min_amount}, max_amount={max_amount}, "
          f"start_date={start_date}, end_date={end_date}, vendor_pattern={vendor_pattern}, "
          f"skip={skip}, limit={limit}")

    receipts = crud.search_receipts(
        db=db,
        keyword=keyword,
        min_amount=min_amount,
        max_amount=max_amount,
        start_date=start_date,
        end_date=end_date,
        vendor_pattern=vendor_pattern,
        skip=skip,
        limit=limit
    )
    return [ReceiptResponse.model_validate(r) for r in receipts]

# 2. Next most specific static path
@router.get("/receipts", response_model=List[ReceiptResponse])
def get_all_receipts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all receipt records from the database.
    This endpoint must come BEFORE /receipts/{receipt_id}.
    """
    receipts = crud.get_receipts(db, skip=skip, limit=limit)
    return [ReceiptResponse.model_validate(r) for r in receipts]


# 3. Dynamic path last (because it's more general and can capture other strings)
@router.get("/receipts/{receipt_id}", response_model=ReceiptResponse)
def get_single_receipt(receipt_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single receipt record by its ID.
    """
    receipt = crud.get_receipt(db, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return ReceiptResponse.model_validate(receipt)

# --- Other CRUD and Algorithmic Endpoints (order less critical if they don't conflict with preceding ones) ---

@router.put("/receipts/{receipt_id}", response_model=ReceiptResponse)
def update_single_receipt(receipt_id: int, update_data: ReceiptUpdate, db: Session = Depends(get_db)):
    update_data_dict = update_data.model_dump(exclude_unset=True)

    updated_receipt = crud.update_receipt(db, receipt_id, update_data_dict)
    if not updated_receipt:
        raise HTTPException(status_code=404, detail="Receipt not found or no changes made")
    return ReceiptResponse.model_validate(updated_receipt)

@router.delete("/receipts/{receipt_id}", status_code=204)
def delete_single_receipt(receipt_id: int, db: Session = Depends(get_db)):
    success = crud.delete_receipt(db, receipt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return {"message": "Receipt deleted successfully"}

@router.get("/receipts/sort", response_model=List[ReceiptResponse])
def sort_receipts_api(
    sort_by: str = Query(..., description="Field to sort by: 'amount', 'date', or 'vendor'"),
    sort_order: str = Query("asc", description="Sort order: 'asc' or 'desc'"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Sort receipts by a specified field (amount, date, or vendor) and order (ascending/descending).
    """
    if sort_by not in ["amount", "date", "vendor"]:
        raise HTTPException(status_code=400, detail="sort_by must be 'amount', 'date', or 'vendor'")
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="sort_order must be 'asc' or 'desc'")

    receipts = crud.sort_receipts(
        db=db,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )
    return [ReceiptResponse.model_validate(r) for r in receipts]

@router.get("/analytics/total-spend", response_model=Dict[str, float])
def get_total_spend_api(db: Session = Depends(get_db)):
    """
    Get the total sum of all receipt amounts.
    """
    total = crud.get_total_spend(db)
    return {"total_spend": total}

@router.get("/analytics/spend-statistics", response_model=Dict[str, Optional[float]])
def get_spend_statistics_api(db: Session = Depends(get_db)):
    """
    Get mean, median, and mode of expenditure.
    """
    stats = crud.get_spend_statistics(db)
    return stats

@router.get("/analytics/vendor-frequency", response_model=Dict[str, int])
def get_vendor_frequency_api(db: Session = Depends(get_db)):
    """
    Get the frequency distribution of vendors.
    """
    frequency = crud.get_vendor_frequency(db)
    return frequency

@router.get("/analytics/monthly-spend-trend", response_model=List[Dict[str, Any]])
def get_monthly_spend_trend_api(db: Session = Depends(get_db)):
    """
    Get monthly spend trends.
    """
    trend = crud.get_monthly_spend_trend(db)
    return trend

@router.get("/analytics/spend-by-category", response_model=List[Dict[str, Any]])
def get_spend_by_category_api(db: Session = Depends(get_db)):
    """
    Get total spend broken down by category.
    """
    spend_by_cat = crud.get_spend_by_category(db)
    return spend_by_cat