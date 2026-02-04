from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import api_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title=settings.APP_NAME,
    description="A comprehensive backend for a modern cafe.",
    debug=settings.DEBUG,
)

# ✅ Open CORS for all
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(api_router)

app.mount(
    settings.MEDIA_URL,
    StaticFiles(directory=settings.MEDIA_ROOT),
    name="media",
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Cafe Management System API"}


# To run: uvicorn app.main:app --reload
