from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from authlib.integrations.flask_client import OAuth

mongo = PyMongo()
jwt = JWTManager()
oauth = OAuth()