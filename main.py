import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

# Import backend modules
from app.nlp import process_command, reminders_mgr

app = FastAPI(title="Riko Advanced Voice Assistant API")

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Pydantic Models
class CommandRequest(BaseModel):
    text: str

class ReminderRequest(BaseModel):
    text: str
    time: Optional[str] = "Today"

# --- API ROUTES ---

@app.post("/api/command")
async def handle_voice_command(request: CommandRequest):
    """Parses verbal command and triggers appropriate backend actions using LangChain + Gemini."""
    try:
        result = process_command(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Processing Error: {str(e)}")

@app.get("/api/reminders")
async def get_reminders():
    """Returns all scheduled reminders."""
    return reminders_mgr.get_all()

@app.post("/api/reminders")
async def add_reminder(request: ReminderRequest):
    """Creates a new reminder manually from the UI dashboard."""
    if not request.text:
        raise HTTPException(status_code=400, detail="Reminder text cannot be empty.")
    reminder = reminders_mgr.add(request.text, request.time)
    return reminder

@app.delete("/api/reminders/{reminder_id}")
async def delete_reminder(reminder_id: str):
    """Deletes a reminder by ID."""
    success = reminders_mgr.delete(reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found.")
    return {"status": "success", "message": "Reminder successfully deleted."}


# --- STATIC SITE SERVING ---
# Mount the public web application files directory
public_dir = os.path.join(os.path.dirname(__file__), "public")
if not os.path.exists(public_dir):
    os.makedirs(public_dir)

# Mounts the public folder to host the HTML page at the root route `/`
app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")

