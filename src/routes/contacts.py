import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.schemas import ContactBase, ContactCreate, ContactInDB, ContactUpdate
from src.repository import contacts as repository_contacts
from sqlalchemy import or_, select
from src.database.models import Contact, User
from datetime import date, timedelta
from src.services.auth import auth_service

# Создание логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Создание обработчика для вывода логов в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Создание форматировщика для логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Добавление обработчика к логгеру
logger.addHandler(console_handler)

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=list[ContactInDB])
async def get_contacts(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
    ):
        contacts = await repository_contacts.get_contacts(limit, offset, db, current_user)
        return contacts


@router.post("/", response_model=ContactInDB, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Create a new contact.
    """
    try:
        logger.debug(f"Received contact data for creation: {contact_data}")
        contact = await repository_contacts.create(contact_data, db, current_user)
        logger.debug(f"Contact created successfully: {contact}")
        return contact
    except HTTPException as he:
        logger.error(f"HTTP error while creating contact: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while creating contact: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.get("/birthday", response_model=list[ContactInDB])
async def get_birthdays(
    days: int = Query(7, ge=7),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_birthdays(days, db, current_user)
    return contacts


@router.get("/search", response_model=list[ContactInDB])
async def serch(
    first_name: str = None,
    last_name: str = None,
    email: str = None,
    skip: int = 0,
    limit: int = Query(default=10, le=100, ge=10),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    contacts = await repository_contacts.search(first_name, last_name, email, skip, limit, db, current_user)
    return contacts
    
@router.get("/{contact_id}", response_model=ContactInDB)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact(contact_id, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.put("/{contact_id}")
async def update_contact(
    body: ContactUpdate,
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_contact(contact_id, body, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.delete_contact(contact_id, db, current_user)
    return contact








