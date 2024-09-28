from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.product.product import Product, ChangeLog
from schema.product.product_schema import ProductCreate


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, product: ProductCreate) -> Product:
        db_product = Product(
            name=product.name,
            code=product.code,
            image=product.image,
            stock=product.stock,
            brand=product.brand,
            model=product.model,
            mt=product.mt,
            m2=product.m2,
            m3=product.m3,
            ton=product.ton,
            kg=product.kg,
            adet=product.adet,
            added_by=product.added_by,
            date_added=product.date_added,
            delivered_by=product.delivered_by,
            delivered_to=product.delivered_to,
            description=product.description,
            warehouse=product.warehouse
        )
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def get_all(self):
        return self.db.query(Product).all()

    def get_by_code(self, code: str):
        return self.db.query(Product).filter(Product.code == code).first()

    def delete(self, product_id: int):
        db_product = self.db.query(Product).filter(Product.id == product_id).first()
        if db_product:
            self.db.delete(db_product)
            self.db.commit()
            return True
        return False

    def get_changed_fields(self, old_data, new_data):
        changes = []
        for field, new_value in new_data.items():
            old_value = getattr(old_data, field, None)
            if new_value != old_value:
                changes.append({
                    "field": field,
                    "old_value": old_value,
                    "new_value": new_value
                })
        return changes

    def log_changes(self, product_code: str, changes: list, updated_by: str):
        for change in changes:
            log_entry = ChangeLog(
                product_code=product_code,
                updated_by=updated_by,
                field=change["field"],
                old_value=str(change["old_value"]),
                new_value=str(change["new_value"])
            )
            self.db.add(log_entry)
        self.db.commit()

    def update_product(self, product_code: str, product_data: dict, updated_by: str):
        product = self.db.query(Product).filter(Product.code == product_code).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        changes = self.get_changed_fields(product, product_data)

        for change in changes:
            setattr(product, change["field"], change["new_value"])

        self.db.commit()

        self.log_changes(product_code, changes, updated_by)

        self.db.refresh(product)
        return product


    def update_stock_out_product(self, product_code: str, product_data: dict, updated_by: str):
        product = self.db.query(Product).filter(Product.code == product_code).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        changes = self.get_changed_fields(product, product_data)

        for change in changes:
            setattr(product, change["field"], change["new_value"])

        self.db.commit()

        self.log_changes(product_code, changes, updated_by)

        self.db.refresh(product)

        return product
