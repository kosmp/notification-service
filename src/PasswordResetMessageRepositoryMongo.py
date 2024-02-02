from src.schemas import PasswordResetMessageSchemaBase
from src.abstract_repository import AbstractRepository
from pymongo import database


class PasswordResetMessageRepositoryMongo(AbstractRepository):
    collection: str = "password_reset_msg_collection"

    def __init(self, db: database):
        self.db = db

    async def add_one(self, restore_pass_doc: PasswordResetMessageSchemaBase):
        result = await self.db[self.collection].insert_one(
            restore_pass_doc.model_dump()
        )
        return result.inserted_id

    async def delete_one(
        self, restore_password_message: PasswordResetMessageSchemaBase
    ) -> bool:
        result = await self.db[self.collection].delete_one(
            {"user_id": restore_password_message.user_id}
        )

        if result.deleted_count != 1:
            return False
        return True
