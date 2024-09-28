from sqlalchemy.orm import Session

from models.user.user import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, hashed_password: str, name: str):
    db_user = User(email=email, hashed_password=hashed_password, name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
