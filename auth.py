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

def NameAndEmailAreFree(name:str, email:str):
    userExistsName = db.users.find({'name': name})
    userExistsEmail = db.users.find({'email': email})
    if userExistsName.count() > 0 or userExistsEmail.count() > 0:
        return False
    return True

def checkTokenForValidity(token:str):
    data = decodeToken(token)
    if data['exp'] > datetime.utcnow():
        return data
    return False

def getUserByToken(token:str):
    decodedToken = decodeToken(token)
    if decodedToken is not False:
        user = db.users.find_one({'name': user['name']})
        if user:
            return user
    return False

def tokenIsValid(name:str,email:str):
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

def getCoursesList():
    courses = db.courses.find()
    return courses

def getUserCourses(user:dict):
    courses = db.courses.find({'participants': { "$in" : user}})
    return courses

def updateCourseParameter(name:str, parameter:str, newValueOfParameter:str):
    course = db.courses.find_one({'name': name})
    if course:
        try:
            db.courses.update_one({'name': name}, {'$set': {parameter: newValueOfParameter}})
            return True
        except:
            return False
    return False

def deleteExcitingCourse(name:str):
    courseIsDeleted = db.courses.delete_one({'name': name})
    if courseIsDeleted.deleted_count == 1:
        return True
    return False

def isStudent(user:dict):
    if user['permissions'] == 0:
        return True
    return False

def isLecturer(user:dict):
    if user['permissions'] == 1:
        return True
    return False

def isAdmin(user:dict):
    if user['permissions'] == 2:
        return True
    return False