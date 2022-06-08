from datetime import timedelta,datetime
from jose import jwt
from passlib.context import CryptContext
from config import JWT_SECRET
from database import db

hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")

def createAccessToken(user:dict):
    AccessToken = jwt.encode({'name': user['name'], '_id':user['_id'], 'permissions':user['permissions'], 'exp':datetime.utcnow() + timedelta(hours=1)}, JWT_SECRET, algorithm='HS256')
    return AccessToken

def decodeToken(token:str):
    decodedToken = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    return decodedToken

def createRefreshToken(user:dict):
    RefreshToken = jwt.encode({'_id':user['_id'], 'exp':datetime.utcnow() + timedelta(days=30)}, JWT_SECRET, algorithm='HS256')
    return RefreshToken

def checkAccessTokenForValidity(token:str):
    data = decodeToken(token)
    if data is not False:
        return data
    return False

def checkRefreshTokenForValidity(data:str):
    if data['exp'] < datetime.utcnow():
        return False
    return True

def getUserByToken(token:str):
    user = decodeToken(token)
    if user is not False:
        user = db.users.find_one({'name': user['name']})
        if user:
            return user
    return False

def checkForUserWithExistingCredentials(name:str,email:str):
    foundUsers = db.users.find({'name': name, 'email': email})
    foundArray = []
    for foundUser in foundUsers:
        foundArray.append(foundUser)
    if len(foundArray) > 0:
        return True
    return False

def authenticateUser(name:str, password:str):
    user = db.users.find_one({'name': name})
    if user:
        if verifyPassword(password, user['password']):
            return True
    return False

def InitializeUser(name:str, email:str, password:str):
    hashedPassword = hashPassword(password)
    user = {'name':name,'password':hashedPassword,'email':email,'timestamp':datetime.utcnow(),'courses':[],'level':1,'permissions':0}
    try:
        db.users.insert_one(user)
        return True
    except:
        return False
    
def hashPassword(password:str):
    return hasher.hash(password)

def verifyPassword(password:str, hashedPassword:str):
    return hasher.verify(password, hashedPassword)

def initializeCourse(name:str, description:str, tags:list, lecturer:list, lectureHours:list, courseLength:str, courseStart:str, courseEnd:str, token:str):
    course = {'name':name,'description':description,'tags':tags,'lecturer':lecturer,'lectureHours':lectureHours,'courseLength':courseLength,'courseStart':courseStart,'courseEnd':courseEnd,'timestamp':datetime.utcnow()}
    try:
        db.courses.insert_one(course)
        return True
    except:
        return False

def updateCourseParameter(name:str, parameter:str, newValueOfParameter:str):
    course = db.courses.find_one({'name': name})
    if course:
        try:
            db.courses.update_one({'name': name}, {'$set': {parameter: newValueOfParameter}})
            return True
        except:
            return False
    return False