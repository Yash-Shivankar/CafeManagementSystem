from fastapi import FastAPI
from app.core.config import settings
from app.routes import api_router

app = FastAPI(
    title=settings.APP_NAME,
    description="A comprehensive backend for a modern cafe.",
    debug=settings.DEBUG,
)

app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Cafe Management System API"}


# To run: uvicorn app.main:app --reload
