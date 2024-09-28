from typing import List, Optional

from pydantic import BaseModel


class Product(BaseModel):
    name: str
    stockOut: int
    deliveredTo: Optional[str] = None
    unit: Optional[str] = None
    code: Optional[str] = None


class InvoiceData(BaseModel):
    jobName: str
    fullAddress: str
    district: str
    creationDate: str
    institution: str
    preparedBy: str
    responsiblePerson: str
    products: List[Product]


class StockOutRequest(BaseModel):
    code: str
    stock_out: int
    unit: str


class StockOutRequestList(BaseModel):
    products: list[StockOutRequest]


class PDFFileData(BaseModel):
    file: str
    fileName: str
