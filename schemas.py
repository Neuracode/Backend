from pydantic import BaseModel

class UserInfoRegister(BaseModel):
    name: str
    password: str
    email: str

class UserInfoLogin(BaseModel):
    name: str
    password: str
   
class Authorization(BaseModel):
    token: str
 
class CredentialChanger(BaseModel):
    _id: int
    parameter: str
    newParameter: str
    token: str