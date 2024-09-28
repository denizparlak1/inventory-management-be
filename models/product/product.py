from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from db.db import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    code = Column(String, unique=True, index=True)
    image = Column(String, nullable=True)
    stock = Column(Integer)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    mt = Column(Integer, nullable=True)
    m2 = Column(Integer, nullable=True)
    m3 = Column(Integer, nullable=True)
    ton = Column(Integer, nullable=True)
    kg = Column(Integer, nullable=True)
    adet = Column(Integer, nullable=True)
    added_by = Column(String)
    date_added = Column(String)
    delivered_by = Column(String, nullable=True)
    delivered_to = Column(String, nullable=True)
    description = Column(String, nullable=True)
    warehouse = Column(String, nullable=True)



class ChangeLog(Base):
    __tablename__ = "change_logs"

    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String)
    updated_by = Column(String)
    field = Column(String)
    old_value = Column(String)
    new_value = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)