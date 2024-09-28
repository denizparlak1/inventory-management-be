from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from auth.auth import AuthHandler, pwd_context
from auth.helper import get_current_user, create_access_token
from db.db import get_db
from models.user.user import User
from repository.user.user_repository import get_user_by_email, create_user
from schema.auth.schema import SignInModel, SignUpModel, ChangePasswordRequest

router = APIRouter()

auth_handler = AuthHandler()


@router.post("/sign-up/")
def signup(sign_up_data: SignUpModel, db: Session = Depends(get_db)):
    user = get_user_by_email(db, sign_up_data.email)

    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth_handler.get_password_hash(sign_up_data.password)

    create_user(db, email=sign_up_data.email, hashed_password=hashed_password, name=sign_up_data.name)

    return {"message": "User registered successfully"}


@router.post("/sign-in/")
def signin(sign_in_data: SignInModel, db: Session = Depends(get_db)):
    user = get_user_by_email(db, sign_in_data.email)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not auth_handler.verify_password(sign_in_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email, "name": user.name}
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/change-password/")
async def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    hashed_new_password = auth_handler.get_password_hash(request.new_password)
    current_user.hashed_password = hashed_new_password
    db.commit()
    return {"success": True, "message": "Şifre başarıyla değiştirildi"}
