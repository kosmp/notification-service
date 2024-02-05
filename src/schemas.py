from datetime import datetime

from pydantic import BaseModel


class PasswordResetMessageSchemaBase(BaseModel):
    email: str
    user_id: str
    reset_link: str
    publishing_date: datetime
