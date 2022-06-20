from config import DATABASE_URL
from pymongo import MongoClient
from umongo import Document, fields
from umongo.frameworks import PyMongoInstance

client = MongoClient(DATABASE_URL)

db = client.main
odm = PyMongoInstance(db) # ODM stands for Object Data Mapper (Equivalent to an ORM for a relational database)

@odm.register
class Users(Document):
    name = fields.StringField(required=True, unique=True)
    password = fields.StringField(required=True)
    email = fields.EmailField(required=True, unique=True)
    timestamp = fields.DateTimeField(required=True,default_now=True)
    courses = fields.ListField(fields.ReferenceField('Courses'))
    level = fields.IntField(default=1)
    permissions = fields.IntegerField(default=0)
    hoursDone = fields.FloatField(default=0)
    class Meta:
        collection_name = "users"
Users.ensure_indexes()

@odm.register
class Courses(Document):
    name = fields.StringField(required=True, unique=True)
    lecturer = fields.ReferenceField('Users')
    description = fields.StringField(default="No description for the course yet..")
    tags = fields.ListField(fields.StringField())
    participants = fields.ListField(fields.ReferenceField('Users'))
    lectureHours = fields.DateTimeField(required=True)
    courseLength = fields.IntField(required=True)
    courseStart = fields.DateTimeField(required=True)
    courseEnd = fields.DateTimeField(required=True)
    class Meta:
        collection_name = "courses"
Courses.ensure_indexes()

@odm.register
class BlogPosts(Document):
    name = fields.StringField(required=True, unique=True)
    content = fields.StringField(required=True)
    timestamp = fields.DateTimeField(required=True,default_now=True)
    author = fields.ReferenceField('Users')
    class Meta:
        collection_name = "blogposts"
BlogPosts.ensure_indexes()

@odm.register
class Messages(Document):
    name = fields.ReferenceField('Users',required=True)
    content = fields.StringField(required=True)
    timestamp = fields.DateTimeField(required=True,default_now=True)
    class Meta:
        collection_name = "messagelist"
Messages.ensure_indexes()
        
@odm.register
class Tasks(Document):
    title = fields.StringField(required=True)
    fulfiller = fields.ReferenceField('Users')
    description = fields.StringField(required=True)
    timestamp = fields.DateTimeField(required=True,default_now=True)
    length = fields.IntegerField(required=True)
    approved = fields.BooleanField(default=False)
    class Meta:
        collection_name = "tasks"
Tasks.ensure_indexes()