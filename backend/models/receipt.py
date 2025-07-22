from pydantic import BaseModel, Field
from typing import Optional

class Receipt(BaseModel):
    vendor: str = Field(..., description="Name of the vendor or biller")
    date: str = Field(..., description="Date of transaction or billing period")
    amount: float = Field(..., description="Amount on the receipt or bill")
    category: Optional[str] = Field(None, description="Category (optional, vendor-mapped)")
    currency: Optional[str] = Field(None, description="Currency symbol or code")
    language: Optional[str] = Field(None, description="Language detected (optional)")