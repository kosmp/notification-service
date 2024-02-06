from pymongo import MongoClient

from src.PasswordResetMessageRepositoryMongo import PasswordResetMessageRepositoryMongo
from src.config import settings

client = MongoClient(
    f"mongodb://{settings.mongodb_root_username}:{settings.mongodb_root_password}@{settings.mongodb_primary_host}:{settings.mongodb_port}?authSource=admin&directConnection=true"
)

db = client[settings.mongo_initdb_database]

mongo_repository = PasswordResetMessageRepositoryMongo()


def get_session():
    with client.start_session() as session, session.start_transaction():
        yield session
