from pydantic import BaseModel, Field


class SignInModel(BaseModel):
    email: str
    password: str


class SignUpModel(BaseModel):
    email: str
    password: str
    name:str


class ChangePasswordRequest(BaseModel):
    new_password: str
