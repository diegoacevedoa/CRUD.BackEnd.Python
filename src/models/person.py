from sqlmodel import SQLModel, Field


class Person(SQLModel, table=True):
    __tablename__ = "Persona"  # asegura que el nombre coincida con la tabla real
    IdPersona: int | None = Field(default=None, primary_key=True)
    NoDocumento: str = Field(max_length=50)
    Nombres: str = Field(max_length=100)
    Apellidos: str = Field(max_length=100)
