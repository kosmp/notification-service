from pymongo import MongoClient

from src.adapters.PasswordResetMessageRepositoryMongo import (
    PasswordResetMessageRepositoryMongo,
)
from src.core.config import settings

client = MongoClient(
    f"mongodb://{settings.mongodb_root_username}:{settings.mongodb_root_password}@{settings.mongodb_primary_host}:{settings.mongodb_port}/?replicaset={settings.mongodb_replica_set_name}"
)

db = client[settings.mongo_initdb_database]

mongo_repository = PasswordResetMessageRepositoryMongo(
    db, client, settings.mongodb_collection_name
)
