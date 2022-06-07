from config import DATABASE_URL
from pymongo import MongoClient
from umongo import Document, fields
from umongo.frameworks import PyMongoInstance

client = MongoClient(DATABASE_URL)

db = client.main
odm = PyMongoInstance(db) # ODM stands for Object Data Mapper (Equivalent to an ORM for a relational database)

@odm.register
class User(Document):
    name = fields.StringField(required=True, unique=True)
    password = fields.StringField(required=True)
    email = fields.EmailField(required=True, unique=True)
    timestamp = fields.DateTimeField(required=True,default_now=True)
    courses = fields.ListField(fields.ReferenceField('Course'))
    level = fields.IntField(default=1)
    permissions = fields.IntegerField(default=0)
    class Meta:
        collection_name = "users"
User.ensure_indexes()

@odm.register
class Course(Document):
    name = fields.StringField(required=True, unique=True)
    lecturer = fields.ReferenceField('User')
    description = fields.StringField(default="No description for the course yet..")
    tags = fields.ListField(fields.StringField())
    participants = fields.ListField(fields.ReferenceField('User'))
    lectureHours = fields.DateTimeField(required=True)
    courseLength = fields.IntField(required=True)
    courseStart = fields.DateTimeField(required=True)
    courseEnd = fields.DateTimeField(required=True)
    class Meta:
        collection_name = "courses"
Course.ensure_indexes()

@odm.register
class BlogPosts(Document):
    name = fields.StringField(required=True, unique=True)
    content = fields.StringField(required=True)
    timestamp = fields.DateTimeField(required=True,default_now=True)
    author = fields.ReferenceField('User')
    class Meta:
        collection_name = "blogposts"
BlogPosts.ensure_indexes()

@odm.register
class Messages(Document):
    name = fields.ReferenceField('User',required=True)
    content = fields.StringField(required=True)
    timestamp = fields.DateTimeField(required=True,default_now=True)
    class Meta:
        collection_name = "messagelist"
Messages.ensure_indexes()