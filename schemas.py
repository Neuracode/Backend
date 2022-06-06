from pydantic import BaseModel

class UserInfoRegister(BaseModel):
    name: str
    password: str
    email: str

class UserInfoLogin(BaseModel):
    name: str
    password: str
