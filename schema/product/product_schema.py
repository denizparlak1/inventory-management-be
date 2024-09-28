from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    code: str
    image: Optional[str] = None
    stock: Optional[int] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    mt: Optional[int] = None
    m2: Optional[int] = None
    m3: Optional[int] = None
    ton: Optional[int] = None
    kg: Optional[int] = None
    adet: Optional[int] = None
    added_by: str
    date_added: str
    delivered_by: Optional[str] = None
    delivered_to: Optional[str] = None
    description: Optional[str] = None
    warehouse: Optional[str] = None

    class Config:
        orm_mode = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    stock: Optional[int] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    mt: Optional[int] = None
    m2: Optional[int] = None
    m3: Optional[int] = None
    ton: Optional[int] = None
    kg: Optional[int] = None
    adet: Optional[int] = None
    delivered_by: Optional[str] = None
    delivered_to: Optional[str] = None
    description: Optional[str] = None
    warehouse: Optional[str] = None

    class Config:
        orm_mode = True


class ProductDeleteResponse(BaseModel):
    message: str


class ChangeLog(BaseModel):
    id: int
    product_code: str
    updated_by: str
    field: str
    old_value: str
    new_value: str
    timestamp: datetime

    class Config:
        orm_mode = True


class LowStockProductResponse(BaseModel):
    name: str
    code: str
    unit: Optional[str]
    value: int