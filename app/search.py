import requests
import urllib.parse
from langchain_core.tools import tool

@tool
def google_search(query: str) -> str:
    """
    Search Google and the web for information on general knowledge, Wikipedia topics, current events, or people.
    Use this tool when the user asks "who is...", "what is...", "tell me about...", or asks to search the web/Google.
    
    Parameters:
    - query: The search query or question to look up.
    """
    cleaned_query = query.strip()
    if not cleaned_query:
        return "Please specify what you would like to search for."

    try:
        # We query the Wikipedia Page Summary API which returns high-quality, structured summary extracts
        # without requiring any API keys or credentials.
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(cleaned_query)}"
        headers = {'User-Agent': 'RikoVoiceAssistant/1.0 (contact@example.com)'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            extract = data.get("extract", "")
            if extract:
                # Truncate to reasonable size for voice responses
                if len(extract) > 400:
                    extract = extract[:397] + "..."
                return extract
            return f"Search for '{cleaned_query}' returned no summary."
        elif response.status_code == 404:
            return f"I couldn't find any articles matching '{cleaned_query}' on the web."
        else:
            return f"Sorry, I had trouble performing the search for '{cleaned_query}'."
    except Exception as e:
        return f"I encountered an error searching for '{cleaned_query}': {str(e)}"
