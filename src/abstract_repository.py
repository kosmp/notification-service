from abc import ABC, abstractmethod


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, restore_password_message):
        pass

    @abstractmethod
    async def delete_one(self, restore_password_message):
        pass
