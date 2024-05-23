from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from src.user_schemas import UserResponse

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date | None = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    pass

class ContactInDB(ContactBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user: UserResponse

    class Config:
        orm_mode = True
