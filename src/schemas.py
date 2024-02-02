from datetime import datetime

from pydantic import BaseModel, EmailStr


class PasswordResetMessageSchemaBase(BaseModel):
    email: EmailStr
    reset_link: str
    publishing_date: datetime
