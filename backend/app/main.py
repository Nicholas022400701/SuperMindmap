from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, SessionLocal
from app.db import models, crud
from app.api import endpoints

# This will create the tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Super Mind Map System")

# Set up CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """
    Event handler for application startup.
    - Creates database tables.
    - Ensures the ObjectRoot node exists.
    """
    db = SessionLocal()
    try:
        crud.get_or_create_object_root(db)
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Super Mind Map System API"}

# Include the API router
app.include_router(endpoints.router, prefix="/api")
