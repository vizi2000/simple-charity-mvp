from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

from app.routes import organization
from app.routes.payments_working import router as payments_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Simple Charity MVP",
    description="Single organization charity donation platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://192.168.100.114:5173",
        "http://192.168.100.114:5174",
        "http://194.181.240.37:5174",
        os.getenv("FRONTEND_BASE_URL", "http://localhost:5173"),
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/assets", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(organization.router)
app.include_router(payments_router)

@app.get("/")
async def root():
    return {
        "message": "Simple Charity MVP API",
        "version": "1.0.0",
        "organization": "Misjonarze Parafia Świętej Rodziny"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)