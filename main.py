import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import config

app = FastAPI(title=config.APP_NAME)

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
async def get_status():
    """Simple status check endpoint."""
    return {
        "status": "online",
        "app_name": config.APP_NAME,
        "gemini_api_configured": bool(config.GEMINI_API_KEY)
    }
