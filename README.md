# Riko Voice Assistant

An advanced voice assistant built using LangChain, Gemini LLM (Google Generative AI), and FastAPI.

## Tech Stack
* **Backend**: FastAPI (Python)
* **LLM Orchestration**: LangChain (`langchain-google-genai`)
* **LLM Model**: Gemini 1.5/2.5 Flash
* **Frontend**: Vanilla HTML / CSS / JS with a modern glassmorphism design

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
4. Create a `.env` file in the root directory and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your-gemini-api-key-here
   ```
5. Run the FastAPI development server:
   ```powershell
   uvicorn main:app --reload
   ```
