from contextlib import asynccontextmanager

import aioboto3
from src.config import settings


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
