from contextlib import asynccontextmanager

import aioboto3
from pymongo import MongoClient, database

from src.config import settings


def get_db() -> database:
    db_client = MongoClient(
        f"mongodb://{settings.mongo_initdb_root_username}:{settings.mongo_initdb_root_password}@{settings.mongodb_host}:{settings.mongodb_port}"
    )
    db_name = settings.mongo_initdb_database
    return db_client[db_name]


session = aioboto3.Session()


@asynccontextmanager
async def aws_client(service):
    async with session.client(
        service,
        endpoint_url=settings.localstack_endpoint_url,
        aws_access_key_id=settings.localstack_access_key_id,
        aws_secret_access_key=settings.localstack_secret_access_key,
        region_name="eu-central-1",
    ) as client:
        yield client
