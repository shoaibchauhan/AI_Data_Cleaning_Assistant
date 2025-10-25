import os
from fastapi import FastAPI
from app import routes
from app.database import engine, Base
from app.models import user, file_upload, cleaning_history
from app.routes import auth  # Ensure models are loaded

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "AI Data Cleaning Assistant backend is working!"}

app.include_router(auth.router)
app.include_router(routes.clean.router)
app.include_router(routes.upload.router)

# Create all tables (or check if they exist)
@app.on_event("startup")
async def on_startup():
    """Run once when the server starts."""
    # Ensure uploads directory exists
    os.makedirs("app/static/uploads", exist_ok=True)

    # Create database tables if not already created
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)