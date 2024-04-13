from contextlib import contextmanager

from pymongo.errors import PyMongoError

from src.logging_config import logger
from src.ports.schemas import PasswordResetMessageSchemaBase
from src.ports.abstract_repository import AbstractRepository


class PasswordResetMessageRepositoryMongo(AbstractRepository):
    def __init__(self, db, client, collection):
        self.db = db
        self.client = client
        self.collection = collection

    @contextmanager
    def add_one(self, restore_pass_doc: PasswordResetMessageSchemaBase):
        try:
            with self.client.start_session() as session:
                with session.start_transaction():
                    self.db[self.collection].insert_one(restore_pass_doc.model_dump())
                    yield
                    logger.info("Successfully saved document to database.")
        except PyMongoError as err:
            logger.error(f"Error while inserting to MongoDB: {err}")
