# CRUD.BackEnd.Python

CRUD de BackEnd en lenguaje de programación Python y base de datos PostgreSQL

PASOS PARA DESARROLLARLO

1- Instalar Python para windows desde la web oficial: https://www.python.org/

2- Crear la carpeta del proyecto y ubicarse en esta en la consola

3- Crear el entorno virtual para que los paquetes instalados no afecten los
   otros proyectos de Python: python -m venv .venv

4- Activamos el entorno virtual en una ventana bash: source .venv/Scripts/activate

5- Instalamos fastapi: pip install "fastapi[standard]"

6- Actualizamos la versión de pip: python -m pip install --upgrade pip

7- Instalamos SQLModel: pip install sqlmodel

8- Instalamos asyncpg: pip install asyncpg

9- Instalamos pydantic-settings: pip install pydantic-settings

10- Guardamos requerimientos en el archivo requirements.txt: pip freeze > requirements.txt

11- Instalar paquetes desde el archivo requirements.txt (Esto se hace cuando
   no se ha instalado nada, es opcional): pip install -r requirements.txt

12- Crear archivo carpeta src para agregar los archivos del proyecto

13- Crear archivo de inicio del proyecto llamado __init__.py en la carpeta src:

    from fastapi import FastAPI

    app = FastAPI(title="Api Personas", description="A CRUD with Python", openapi_tags=[{"name":"Main", "description": "Main routes" }])

    @app.get("/", tags=["Main"])
    def read_root():
        return {"Hello": "World"}

14- Ejecutamos el proyecto: fastapi dev src/

15- Creamos variable de entorno .env y agregamos la conexión a la base de datos afuera de la carpeta src:

    DATABASE_URL=postgresql+asyncpg://postgres:Medellin1*@localhost:5432/Persona

16- Creamos archivo config.py con el acceso a las variables de entorno del archivo .env en la carpeta src:

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()

# print(Config.model_dump())


17- Crear nueva carpeta llamada database en la carpeta src

18- Crear adentro de la carpeta database, el archivo person.py:

from sqlmodel import create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import Config


async_engine = AsyncEngine(create_engine(url=Config.DATABASE_URL, echo=True))


async def init_db():
    async with async_engine.begin() as conn:
        statement = text("SELECT 'Hello Data Base';")

        result = await conn.execute(statement)

        print(result.all)


async def get_session() -> AsyncSession:  # type: ignore
    session_db = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_db() as session:
        yield session


19- Modificamos el archivo __init__.py para verificar conexión a la base de datos:

from fastapi import FastAPI
from src.database.database import init_db

app = FastAPI(
    root_path="/api",
    title="Api Personas",
    description="A CRUD with Python",
    openapi_tags=[{"name": "Main", "description": "Main routes"}],
    version="1.0.0",
)


@app.get("/", tags=["Main"])
async def read_root():
    await init_db()
    return {"Hello": "World"}


20- Crear nueva carpeta llamada models en la carpeta src

21- Crear adentro de la carpeta models, el archivo person.py:

from sqlmodel import SQLModel, Field


class Person(SQLModel, table=True):
    __tablename__ = "Persona"  # asegura que el nombre coincida con la tabla real
    IdPersona: int | None = Field(default=None, primary_key=True)
    NoDocumento: str = Field(max_length=50)
    Nombres: str = Field(max_length=100)
    Apellidos: str = Field(max_length=100)


22- Crear nueva carpeta llamada schemas en la carpeta src

23- Crear adentro de la carpeta schemas, el archivo person.py:

from pydantic import BaseModel
from typing import Optional


class BasePerson(BaseModel):
    NoDocumento: str
    Nombres: str
    Apellidos: str


class Person(BasePerson):
    IdPersona: int


class PersonCreate(BasePerson):
    pass


class PersonUpdate(BasePerson):
    pass

24- Creamos nuevo archivo llamado errors.py en la carpeta src:

from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status
from sqlalchemy.exc import SQLAlchemyError


class DatalyException(Exception):
    """This is the base class for all data errors"""

    pass


class DataNotFound(DatalyException):
    """Data Not found"""

    pass


def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:

    def exception_handler(request: Request, exc: DatalyException):

        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        DataNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Data not found",
                "error_code": "data_not_found",
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exc):

        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database__error(request, exc):
        print(str(exc))
        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


25- Crear nueva carpeta llamada services en la carpeta src

26- Crear adentro de la carpeta services, el archivo person.py:

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


27- Crear nueva carpeta llamada routers en la carpeta src

28- Crear adentro de la carpeta routers, el archivo person.py:

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



29- Modificamos archivo __init__.py:

from fastapi import FastAPI
from src.errors import register_all_errors
from src.routers import person
from src.database.person import init_db

app = FastAPI(
    root_path="/api",
    title="Api Personas",
    description="A CRUD with Python",
    openapi_tags=[{"name": "Main", "description": "Main routes"}],
    version="1.0.0",
)

# Errors
register_all_errors(app)

# Routers
app.include_router(person.router)


@app.get("/", tags=["Main"])
async def read_root():
    await init_db()
    return {"Hello": "World"}

30- Ejecutamos el proyecto: fastapi dev src/
