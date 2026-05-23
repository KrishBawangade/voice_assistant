from datetime import datetime
from langchain_core.tools import tool

@tool
def get_current_time_and_date() -> str:
    """
    Retrieves the current local time and date.
    Use this tool when the user asks 'what time is it?', 'what is the date?', 
    'what day is it?', or asks for the current clock status.
    """
    now = datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A, %B %d, %Y")
    return f"It is currently {time_str} on {date_str}."
