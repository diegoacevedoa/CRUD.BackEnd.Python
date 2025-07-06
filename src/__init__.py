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
