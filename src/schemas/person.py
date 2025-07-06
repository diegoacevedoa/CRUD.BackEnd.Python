from pydantic import BaseModel


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
