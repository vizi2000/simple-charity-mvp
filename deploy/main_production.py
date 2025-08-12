from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

from app.routes import organization, payments

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Simple Charity MVP",
    description="Single organization charity donation platform",
    version="1.0.0"
)

# Configure CORS with all necessary origins
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://192.168.100.159",
    "http://192.168.100.159:5173",
    "http://192.168.100.159:5174",
    "https://borgtools.ddns.net",
    "http://borgtools.ddns.net",
    "https://test.ipg-online.com",  # Fiserv test gateway
    "https://prod.emea.api.fiservapps.com",  # Fiserv production
    os.getenv("FRONTEND_BASE_URL", "http://localhost:5173"),
]

# Add any additional origins from environment
extra_origins = os.getenv("CORS_ORIGINS", "").split(",")
for origin in extra_origins:
    if origin.strip():
        allowed_origins.append(origin.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Mount static files
app.mount("/assets", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(organization.router)
app.include_router(payments.router)

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
    # Use environment variables for host and port
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    reload = os.getenv("ENVIRONMENT", "production") == "development"
    
    uvicorn.run(app, host=host, port=port, reload=reload)