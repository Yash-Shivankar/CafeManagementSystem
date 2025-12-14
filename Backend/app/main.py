from fastapi import FastAPI
from app.core.config import settings
from app.routes import auth

app = FastAPI(
    title=settings.APP_NAME,
    description="A comprehensive backend for a modern cafe.",
    debug=settings.DEBUG,
)

app.include_router(auth.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Cafe Management System API"}


# To run: uvicorn app.main:app --reload
