from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.schemas.person import PersonCreate, PersonUpdate
from src.models.person import Person


async def get_persons(session: AsyncSession):
    statement = select(Person)

    result = await session.exec(statement)

    return result.all()


async def get_person(id: int, session: AsyncSession):
    statement = select(Person).where(Person.IdPersona == id)

    result = await session.exec(statement)

    data = result.first()

    return data if data is not None else None


async def create_person(data: PersonCreate, session: AsyncSession):
    data_dict = data.model_dump()

    new_data = Person(**data_dict)

    session.add(new_data)

    await session.commit()

    return new_data


async def update_person(id: int, data: PersonUpdate, session: AsyncSession):
    data_to_update = await get_person(id, session)

    if data_to_update is not None:
        update_data_dict = data.model_dump()

        for k, v in update_data_dict.items():
            setattr(data_to_update, k, v)

        await session.commit()

        return data_to_update
    else:
        return None


async def delete_person(id: int, session: AsyncSession):
    data_to_delete = await get_person(id, session)

    if data_to_delete is not None:
        await session.delete(data_to_delete)

        await session.commit()

        return {}

    else:
        return None
