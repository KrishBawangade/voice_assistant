import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any
from langchain_core.tools import tool
from app import config

class RemindersManager:
    def __init__(self, filepath: str = config.REMINDERS_FILE):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _load_reminders(self) -> List[Dict[str, Any]]:
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _save_reminders(self, reminders: List[Dict[str, Any]]):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(reminders, f, indent=4, ensure_ascii=False)

    def get_all(self) -> List[Dict[str, Any]]:
        """Returns all reminders, sorted by creation time."""
        reminders = self._load_reminders()
        return sorted(reminders, key=lambda x: x.get("created_at", ""), reverse=True)

    def add(self, text: str, time_str: str = None) -> Dict[str, Any]:
        """Creates and saves a new reminder."""
        reminders = self._load_reminders()
        new_reminder = {
            "id": str(uuid.uuid4()),
            "text": text,
            "time": time_str or "Today",
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        reminders.append(new_reminder)
        self._save_reminders(reminders)
        return new_reminder

    def delete(self, reminder_id: str) -> bool:
        """Deletes a reminder by ID."""
        reminders = self._load_reminders()
        initial_length = len(reminders)
        reminders = [r for r in reminders if r["id"] != reminder_id]
        if len(reminders) < initial_length:
            self._save_reminders(reminders)
            return True
        return False

    def clear_all(self) -> int:
        """Clears all reminders from the database."""
        count = len(self._load_reminders())
        self._save_reminders([])
        return count

# Initialize global manager
reminders_mgr = RemindersManager()

@tool
def add_reminder(text: str, time_str: str = "Today") -> str:
    """
    Creates and saves a new reminder for the user.
    Use this tool when the user asks to "remind me to...", "set a reminder for...", or "add a reminder to...".
    
    Parameters:
    - text: The task or reminder content (e.g., "call Mom", "submit assignment").
    - time_str: The time or day of the reminder (e.g., "5 pm", "tomorrow", "Friday"). Defaults to "Today".
    """
    reminder = reminders_mgr.add(text, time_str)
    return json.dumps({
        "status": "success",
        "action": "ADD_REMINDER",
        "reminder": reminder,
        "all_reminders": reminders_mgr.get_all()
    })

@tool
def list_reminders() -> str:
    """
    Retrieves and lists all active reminders scheduled by the user.
    Use this tool when the user asks "what are my reminders?", "list my reminders", or "show reminders".
    """
    all_reminders = reminders_mgr.get_all()
    return json.dumps({
        "status": "success",
        "action": "LIST_REMINDERS",
        "reminders": all_reminders
    })

@tool
def clear_all_reminders() -> str:
    """
    Clears all active reminders from the database.
    Use this tool when the user asks to "clear reminders", "delete all reminders", or "remove my reminders".
    """
    count = reminders_mgr.clear_all()
    return json.dumps({
        "status": "success",
        "action": "CLEAR_REMINDERS",
        "count": count,
        "reminders": []
    })
