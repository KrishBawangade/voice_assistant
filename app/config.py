import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# App Configurations
APP_NAME = "Riko Voice Assistant"
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# Simulated DB Paths
REMINDERS_FILE = os.getenv("REMINDERS_FILE", "reminders.json")
