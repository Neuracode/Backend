from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import db
from schemas import Authorization, CredentialChanger, CredentialChanger, UserInfoLogin, UserInfoRegister
from auth import InitializeUser, authenticateUser, checkAccessTokenForValidity, checkForUserWithExistingCredentials, createAccessToken, checkRefreshTokenForValidity, createRefreshToken, decodeToken, getUserByToken, hashPassword
import uvicorn

app = FastAPI()

app.add_middleware(
CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post('/token/get/{refreshToken}')
async def getToken(refreshToken: str):
    data = decodeToken(refreshToken)
    isValid = checkRefreshTokenForValidity(data)
    if isValid is not False:
        user = db.users.find_one({'name': data['_id']})
        if user:
            token = createAccessToken(user)
        return{'code': 200, 'token': token}
    return{'code': 401, 'message': 'Invalid refresh token'}

@app.get('/users/get/all')
async def getAllUsers(data: Authorization):
    payload = checkAccessTokenForValidity(data.token) 
    if payload is not False:
        if payload['permissions'] == 2:
            userarray = []
            users = db.users.find()
            for user in users:
                userarray.append(user)
            return{"users":userarray}
        return {"code": 401, "message": "You do not have permission to access this resource"}
    return{"code":401, "message":"Invalid access token"}

@app.put('/users/update/{parameter}/{_id}')
async def updateUser(data:CredentialChanger):
    user = getUserByToken(data.token)
    if user is not False:
        db.users.update_one({"_id":user["_id"]},{"$set":{data.parameter:data.newParameter}})
        return{'code':200,'message':f'User\'s {data.parameter} updated to {data.newParameter}.'}
    return{'code':500,'message':'User not updated due to internal error.'}

@app.post('/users/register')
async def registerUser(data:UserInfoRegister):
    if checkForUserWithExistingCredentials(data.name,data.email):
        return{'code':500,'message':'User already exists.'}
    user = InitializeUser(data.name,data.email,data.password)
    if user is not False:
        token = createAccessToken(user)
        refreshToken = createRefreshToken(user)
        return {'code':200,'message':'User registered.','access_token':token,'refresh_token':refreshToken}
    return{'code':500,'message':'User not registered due to internal error.'}

@app.post('/users/login/{name}')
async def loginUser(data:UserInfoLogin):
    if authenticateUser(data.name,data.password):
        user = db.users.find_one({'name': data.name})
        if user is not False:
            token = createAccessToken(user)
            refreshToken = createRefreshToken(user)
            return {'code':200,'message':'User logged in.','access_token':token,'refresh_token':refreshToken}
        return{'code':500,'message':'User not logged in due to internal error.'}
    return {'code':401,'message':'Invalid credentials.'}

if __name__ == '__main__':
    uvicorn.run(app, host='localhost',port=8000,flag='debug')