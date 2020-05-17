from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.models import setup_database
from app.routers import user, cell, lease

load_dotenv()
app = FastAPI()
db = setup_database()

origins = [
    "http://api.noirdjinn.dev",
    "https://api.noirdjinn.dev",
    "http://localhost",
    "http://localhost:3000",
    "https://localhost:3000",
]


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="TakeAndGo",
        version="0.0.4",
        description="Smart bookshelf project",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://raw.githubusercontent.com/Svintsova/TAGdiploma2020/master/public/hselogo.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(user.router, prefix="/user")
app.include_router(cell.router, prefix="/cell")
app.include_router(lease.router, prefix="/lease")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.openapi = custom_openapi
