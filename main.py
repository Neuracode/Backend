from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import db
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

@app.get('/users/get/all')
async def getAllUsers():
    userarray = []
    users = db.users.find()
    for user in users:
        userarray.append(user)
    return{"users":userarray}

@app.put('/users/update/{id}')
async def updateUser():
    return{}

#Endpoints can be added here or in separated in a file