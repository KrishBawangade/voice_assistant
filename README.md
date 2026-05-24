# Riko Voice Assistant

An advanced voice assistant built using LangChain, Gemini LLM (Google Generative AI), and FastAPI. It uses a structured 2-turn agent pipeline to classify intents, run local tools manually, and generate natural, voice-friendly conversational responses.

## Key Features

1. **Intelligent Intent & Tool Selection**: Uses a structured Pydantic schema (`ToolCallDecision`) to ensure Gemini always returns clean, consistent JSON for every turn.
2. **Context Memory**: Maintains a global conversation history stack, feeding the last 6 messages (3 turns) to Gemini to support fluid context tracking (e.g. *"What is the weather in London?"* -> *"Is it raining there?"*).
3. **Celsius Weather Tool**: Fetches metric weather from OpenWeatherMap (or deterministically simulates it) and maps standard API icon codes directly to gorgeous colored CSS gradient cards.
4. **Reminders Tool**: Saves, lists, and deletes active reminders in a local database file (`reminders.json`) dynamically rendered in the UI.
5. **Google/Web Search Tool**: Uses the Wikipedia REST API to scrape extracts for general knowledge queries instantly without requiring API keys.
6. **Time & Date Tool**: Reports local clock time and date dynamically.
7. **Premium Glassmorphic UI**: Features a beautiful neon purple-and-cyan dark theme panel, dynamic sidebar widgets, typing loader animations, and browser-native voice input using the Web Speech API.

## Tech Stack
* **Backend**: FastAPI (Python)
* **LLM Orchestration**: LangChain (`langchain-google-genai` & `langchain-core`)
* **LLM Model**: Gemini 2.5 Flash
* **Frontend**: Vanilla HTML5, CSS3, and JavaScript (ES6)

## Setup Instructions

1. Clone or download this repository.
2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory and add your keys:
   ```env
   GEMINI_API_KEY=your-gemini-api-key-here
   OPENWEATHER_API_KEY=optional-openweather-api-key-here
   ```
5. Run the FastAPI development server:
   ```powershell
   uvicorn main:app --reload
   ```
6. Open your browser and navigate to:
   ```
   http://127.0.0.1:8000/
   ```

## Example Prompts
* *"Hello Riko, how is your day going?"*
* *"What is the weather in Paris?"* (Returns report in Celsius)
* *"Remind me to submit my project tomorrow at 4 PM"*
* *"Show all my reminders"*
* *"Who is Nikola Tesla?"* (Triggers web search)
* *"What time is it right now?"* (Triggers clock tool)

