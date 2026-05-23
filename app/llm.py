from langchain_google_genai import ChatGoogleGenerativeAI
from app import config

def get_llm(model_name: str = "gemini-2.5-flash", temperature: float = 0.5) -> ChatGoogleGenerativeAI:
    """
    Initializes and returns the ChatGoogleGenerativeAI client using the configured API key.
    """
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is not set or is still the default placeholder.\n"
            "Please update the GEMINI_API_KEY in your local .env file."
        )
    
    # Initialize LangChain's Google GenAI Chat model
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=config.GEMINI_API_KEY,
        temperature=temperature
    )
    return llm
