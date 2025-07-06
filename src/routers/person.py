from fastapi import APIRouter, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from src.database.person import get_session
from src.schemas.person import Person, PersonCreate, PersonUpdate
from src.services import person as person_service
from src.errors import DataNotFound


router = APIRouter(prefix="/person", tags=["Personas"])


@router.get("/", response_model=List[Person], status_code=status.HTTP_200_OK)
async def get_persons(session: AsyncSession = Depends(get_session)):
    result = await person_service.get_persons(session)
    return result


@router.get("/{id}", response_model=Person, status_code=status.HTTP_200_OK)
async def get_person(id: int, session: AsyncSession = Depends(get_session)) -> dict:
    result = await person_service.get_person(id, session)

    if result:
        return result
    else:
        raise DataNotFound()


@router.post("/", response_model=Person, status_code=status.HTTP_201_CREATED)
async def create_person(
    data: PersonCreate, session: AsyncSession = Depends(get_session)
) -> dict:
    result = await person_service.create_person(data, session)
    return result


@router.put("/{id}", response_model=Person, status_code=status.HTTP_200_OK)
async def update_person(
    id: int, data: PersonUpdate, session: AsyncSession = Depends(get_session)
) -> dict:
    result = await person_service.update_person(id, data, session)

    if result is None:
        raise DataNotFound()
    else:
        return result


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_person(id: int, session: AsyncSession = Depends(get_session)):
    result = await person_service.delete_person(id, session)

    if result is None:
        raise DataNotFound()
    else:
        return {}
