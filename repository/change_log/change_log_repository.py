from sqlalchemy.orm import Session
from models.product.product import ChangeLog


class ChangeLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_change_logs(self):
        return self.db.query(ChangeLog).all()
