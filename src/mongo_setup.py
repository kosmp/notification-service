from pymongo import MongoClient

from src.PasswordResetMessageRepositoryMongo import PasswordResetMessageRepositoryMongo
from src.config import settings

client = MongoClient(
    f"mongodb://{settings.mongo_initdb_root_username}:{settings.mongo_initdb_root_password}@{settings.mongodb_host}:{settings.mongodb_port}"
)

db = client[settings.mongo_initdb_database]

mongo_repository = PasswordResetMessageRepositoryMongo()
