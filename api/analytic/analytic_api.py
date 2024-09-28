from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from db.db import get_db
from models.product.product import Product, ChangeLog
from schema.product.product_schema import LowStockProductResponse

router = APIRouter()


@router.get("/total-products/")
async def get_total_products(db: Session = Depends(get_db)):
    try:
        total_products = db.query(Product).count()
        return {"total_products": total_products}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching total product count")


@router.get("/out-of-stock-products/")
async def get_out_of_stock_products(db: Session = Depends(get_db)):
    try:
        out_of_stock_count = db.query(Product).filter(Product.stock <= 0).count()
        return {"out_of_stock_products": out_of_stock_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching out of stock product count")


@router.get("/top-5-products/")
async def get_top_5_products(db: Session = Depends(get_db)):
    try:
        top_products = (
            db.query(Product.name, Product.code, func.count(ChangeLog.id).label("action_count"))
            .join(ChangeLog, Product.code == ChangeLog.product_code)
            .group_by(Product.name, Product.code)
            .order_by(func.count(ChangeLog.id).desc())
            .limit(5)
            .all()
        )
        return {"top_products": [{"name": product.name, "code": product.code, "action_count": product.action_count} for
                                 product in top_products]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching top 5 products")


@router.get("/deleted-products/", response_model=Dict[str, int])
async def count_deleted_products(db: Session = Depends(get_db)):
    deleted_count = db.query(ChangeLog).filter(ChangeLog.new_value == "Ürün Silindi").count()

    return {"total_deleted_products": deleted_count}


@router.get("/low-stock-units/", response_model=List[LowStockProductResponse])
async def get_low_stock_units(db: Session = Depends(get_db)):
    products = db.query(Product).all()

    low_stock_products = []

    def is_valid_number(value):
        try:
            return isinstance(float(value), float)
        except (ValueError, TypeError):
            return False

    def convert_to_int(value):
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    for product in products:
        if product.mt and is_valid_number(product.mt) and convert_to_int(product.mt) < 50:
            low_stock_products.append({"name": product.name, "code": product.code, "unit": "MT", "value": product.mt})

        if product.m2 and is_valid_number(product.m2) and convert_to_int(product.m2) < 50:
            low_stock_products.append({"name": product.name, "code": product.code, "unit": "M2", "value": product.m2})

        if product.m3 and is_valid_number(product.m3) and convert_to_int(product.m3) < 50:
            low_stock_products.append({"name": product.name, "code": product.code, "unit": "M3", "value": product.m3})

        if product.ton and is_valid_number(product.ton) and convert_to_int(product.ton) < 50:
            low_stock_products.append({"name": product.name, "code": product.code, "unit": "Ton", "value": product.ton})

        if product.adet and is_valid_number(product.adet) and convert_to_int(product.adet) < 50:
            low_stock_products.append({"name": product.name, "code": product.code, "unit": "Adet", "value": product.adet})

    return low_stock_products
