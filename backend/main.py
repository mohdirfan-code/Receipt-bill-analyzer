# backend/main.py (Complete Code)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.upload import router as upload_router
from backend.db.database import init_db

app = FastAPI()

# Configure CORS (Important: This should be one of the first things after app = FastAPI())
origins = [
    "http://localhost",
    "http://localhost:3000", # React dev server
    "http://localhost:5173", # Vite dev server
    "http://localhost:8501", # Streamlit dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8501",
    "http://127.0.0.1:8000", # If your FastAPI runs on 8000 and frontend on same
    # Add your deployed frontend URL here when you deploy
    # "https://your-deployed-frontend.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CRITICAL: Include your API routers here, BEFORE any generic routes or other potentially conflicting routers ---
app.include_router(upload_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    init_db()
    print("FastAPI application startup: Database initialized.")

# This is a very general root route. It's usually fine if other routes are prefixed properly.
@app.get("/")
def read_root():
    return {"message": "Receipt Bill Analyzer Backend is running!"}