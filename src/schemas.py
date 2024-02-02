from datetime import datetime

from pydantic import BaseModel, EmailStr, UUID4


class PasswordResetMessageSchemaBase(BaseModel):
    email: EmailStr
    user_id: UUID4
    reset_link: str
    publishing_date: datetime
