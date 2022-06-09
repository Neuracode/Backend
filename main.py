from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import db
from schemas import Authorization, CourseAuthorization, CreateCourseAuthorization, CredentialChangeAuthorization, CourseAuthorization, UserInfoLogin, UserInfoRegister
from auth import InitializeUser, NameAndEmailAreFree, authenticateUser, checkTokenForValidity, createAccessToken, createRefreshToken, deleteExcitingCourse, getCoursesList, getUserByToken, initializeCourse, isAdmin, isLecturer, tokenIsValid, updateCourseParameter
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
    return {"This is the root of the API": "--- root ---"}

# --- Basic token init --- #

@app.post('/token/get/{refreshToken}')
async def getToken(refreshToken: str):
    data = checkTokenForValidity(refreshToken)
    if data is not False:
        user = db.users.find_one({'name': data['_id']})
        if user:
            token = createAccessToken(user)
        return {'code': 200, 'token': token}
    return {'code': 401, 'message': 'Invalid refresh token'}

# --- Basic user auth and manipulation --- #

@app.post('/users/register/{name}')
async def registerUser(data:UserInfoRegister):
    if NameAndEmailAreFree(data.name,data.email):
        return {'code':500,'message':'User already exists.'}
    user = InitializeUser(data.name,data.email,data.password)
    if user is not False:
        token = createAccessToken(user)
        refreshToken = createRefreshToken(user)
        return {'code':200,'message':'User registered.','access_token':token,'refresh_token':refreshToken}
    return {'code':500,'message':'User not registered due to internal error.'}

@app.post('/users/login/{name}')
async def loginUser(data:UserInfoLogin):
    if authenticateUser(data.name,data.password):
        user = db.users.find_one({'name': data.name})
        if user is not False:
            token = createAccessToken(user)
            refreshToken = createRefreshToken(user)
            return {'code':200,'message':'User logged in.','access_token':token,'refresh_token':refreshToken}
        return {'code':500,'message':'User not logged in due to internal error.'}
    return {'code':401,'message':'Invalid credentials.'}

@app.put('/users/{name}/{parameter}/update')
async def updateUser(data:CredentialChangeAuthorization):
    user = getUserByToken(data.token)
    if user is not False and user['_id'] == data._id:
        db.users.update_one({"_id":user["_id"]},{"$set":{data.parameter:data.newParameter}})
        return {'code':200,'message':f'User\'s {data.parameter} updated to {data.newParameter}.'}
    return {'code':500,'message':'User not updated due to internal error.'}


# --- Admin features --- #

    # --- Get user info --- #
@app.get('/users/all/get')
async def getAllUsers(data: Authorization):
    payload = tokenIsValid(data.token) 
    if payload is not False:
        if isAdmin(): #This means the user is an admin | I will do a more moderate version for the lecturers in my next commit probably
            userarray = []
            users = db.users.find()
            for user in users:
                userarray.append(user)
            return {"users":userarray}
        return {"code": 401, "message": "You do not have permission to access this resource"}
    return {"code":401, "message":"Invalid access token"}

    # --- Courses init and manipulation --- #

@app.post('/courses/{courseName}/create')
async def createCourse(data:CreateCourseAuthorization):
    user = getUserByToken(data.token)
    if isAdmin(user):
        courseIsCreated = initializeCourse(data.courseName,data.courseDescription,data.courseTags,data.lecturer,data.lectureHours,data.courseLength,data.courseStart,data.courseEnd)
        if courseIsCreated:
            return {'code':200,'message':'Course created.'}
    return {'code':401,'message':'You do not have permission to access this resource.'}

@app.put('/courses/{courseName}/{parameter}/update')
async def updateCourse(data:CourseAuthorization):
    user = getUserByToken(data.token)
    if isAdmin(user):
        courseIsUpdated = updateCourseParameter(data.courseName,data.parameter,data.newParameter)
        if courseIsUpdated:
            return {'code':200,'message':'Course updated.'}
        return {'code':500,'message':'Course not updated due to internal error.'}
    return {'code':401,'message':'You do not have permission to access this resource.'}

@app.delete('/courses/{courseName}/delete')
async def deleteCourse(data:CourseAuthorization):
    user = getUserByToken(data.token)
    if isAdmin(user):
        courseIsDeleted = deleteExcitingCourse(data.courseName)
        if courseIsDeleted:
            return {'code':200,'message':'Course deleted.'}
        return {'code':500,'message':'Course not deleted due to internal error.'}
    return {'code':401,'message':'You do not have permission to access this resource.'}

@app.post('/courses/{courseName}/users/get/all')
async def getAllUsersInCourse(data:CourseAuthorization):
    user = getUserByToken(data.token)
    if isAdmin(user):
        course = db.courses.find_one({'name':data.courseName})
        if course is not None:
            return {'code': 200, 'courseStudents': course['participants']} #return users here
        return {'code': 500, 'message': 'Course not found.'}
    return { 'code': 401, 'message': 'You do not have permission to access this resource.'}

@app.get('/courses/all/get')
async def getAllCourses():
    return { 'code': 200, 'courses': getCoursesList()}
if __name__ == '__main__':
    uvicorn.run(app, host='localhost',port=8000,flag='debug')