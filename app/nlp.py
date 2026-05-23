import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage
from app.llm import get_llm
from app.prompts import get_voice_assistant_prompt

# In-memory global chat history to maintain conversational context
chat_history: List[Any] = []

# Import backend modules
from app.weather import fetch_weather_data
from app.reminders import reminders_mgr
from app.search import google_search
from app.time_tool import get_current_time_and_date

# Pydantic schema for structured output from the first LLM call
class ToolCallDecision(BaseModel):
    tool_to_call: Optional[str] = Field(
        None, 
        description=(
            "The name of the tool to invoke: 'get_current_weather', 'add_reminder', "
            "'list_reminders', 'clear_all_reminders', 'google_search', "
            "'get_current_time_and_date', or null if no tool is needed."
        )
    )
    tool_arguments: Optional[Dict[str, Any]] = Field(
        None, 
        description="The arguments dictionary to pass to the tool (e.g. {'city': 'London'} or {'text': 'call mom'})"
    )
    response: Optional[str] = Field(
        None, 
        description=(
            "Set this to null if a tool is being called. "
            "If no tool is called (e.g., for greetings, general chitchat, or clarification requests), "
            "provide the complete conversational text response here."
        )
    )

def process_command(text: str) -> Dict[str, Any]:
    """
    Processes a command text from the user.
    - Call 1: Obtains a structured decision (JSON object).
    - If a tool is called, it executes the tool manually and performs Call 2 to synthesize
      the final speech response from the tool output.
    - If no tool is called, it directly returns the speech response from Call 1.
    """
    text_lower = text.strip()
    
    # Standard response structure for the frontend
    response_data = {
        "text": text,
        "intent": "UNKNOWN",
        "speech": "I encountered an error processing your request.",
        "data": {},
        "ui_action": None
    }

    if not text_lower:
        response_data["speech"] = "I didn't hear anything. Please try speaking again."
        return response_data

    try:
        # Initialize Gemini LLM with structured output binding for Call 1
        llm = get_llm()
        structured_llm = llm.with_structured_output(ToolCallDecision)
        
        global chat_history

        # Format the chat prompt with sliding history window to balance latency and context
        prompt_template = get_voice_assistant_prompt()
        messages = prompt_template.format_messages(
            chat_history=chat_history[-6:],  # Last 3 turns (6 messages)
            input=text
        )

        # Call 1: Structured decision to identify tool and arguments
        decision = structured_llm.invoke(messages)
        tool_to_call = decision.tool_to_call
        tool_args = decision.tool_arguments or {}

        if tool_to_call:
            tool_output = ""
            action_type = None

            # Execute the correct tool manually based on the decision
            if tool_to_call == "get_current_weather":
                city = tool_args.get("city") or "New York"
                weather_res = fetch_weather_data(city)
                tool_output = json.dumps(weather_res)
                
                response_data["intent"] = "WEATHER"
                response_data["ui_action"] = "UPDATE_WEATHER"
                response_data["data"] = {"weather": weather_res}

            elif tool_to_call == "add_reminder":
                task = tool_args.get("text")
                time_str = tool_args.get("time_str") or "Today"
                if task:
                    task = task[0].upper() + task[1:]
                    time_str = time_str.strip().title()
                    reminder_res = reminders_mgr.add(task, time_str)
                    tool_output = json.dumps({
                        "action": "ADD_REMINDER",
                        "reminder": reminder_res,
                        "reminders": reminders_mgr.get_all()
                    })
                    
                    response_data["intent"] = "REMINDER_ADD"
                    response_data["ui_action"] = "UPDATE_REMINDERS"
                    response_data["data"] = {"reminders": reminders_mgr.get_all()}
                else:
                    tool_output = "Error: Reminder text was empty."

            elif tool_to_call == "list_reminders":
                rems = reminders_mgr.get_all()
                tool_output = json.dumps({
                    "action": "LIST_REMINDERS",
                    "reminders": rems
                })
                
                response_data["intent"] = "REMINDER_LIST"
                response_data["ui_action"] = "UPDATE_REMINDERS"
                response_data["data"] = {"reminders": rems}

            elif tool_to_call == "clear_all_reminders":
                count = reminders_mgr.clear_all()
                tool_output = json.dumps({
                    "action": "CLEAR_REMINDERS",
                    "count": count,
                    "reminders": []
                })
                
                response_data["intent"] = "REMINDER_CLEAR"
                response_data["ui_action"] = "UPDATE_REMINDERS"
                response_data["data"] = {"reminders": []}



            elif tool_to_call == "google_search":
                query = tool_args.get("query")
                if query:
                    search_res = google_search.run(query)
                    tool_output = search_res
                    
                    response_data["intent"] = "WIKIPEDIA"
                    response_data["ui_action"] = None
                    response_data["data"] = {"search_result": search_res}
                else:
                    tool_output = "Error: Search query was empty."

            elif tool_to_call == "get_current_time_and_date":
                time_res = get_current_time_and_date.run({})
                tool_output = time_res
                response_data["intent"] = "TIME_DATE"
                response_data["ui_action"] = None
                response_data["data"] = {}

            # Call 2: Standard LLM call to generate conversational response from the tool output
            second_call_messages = [
                (
                    "system", 
                    "You are Riko, a premium voice assistant. Generate a warm, natural, and concise conversational response for the user "
                    "summarizing the outcome of their request based on the tool's result."
                ),
                (
                    "human", 
                    f"User Request: {text}\nTool Executed: {tool_to_call}\nTool Output: {tool_output}"
                )
            ]
            final_speech = llm.invoke(second_call_messages)
            response_data["speech"] = final_speech.content

        else:
            # No tool to call; direct response from Call 1
            response_data["speech"] = decision.response or "How can I help you?"
            if any(greet in text_lower.lower() for greet in ["hello", "hi", "hey", "good morning", "riko"]):
                response_data["intent"] = "GREETING"

    except Exception as e:
        response_data["speech"] = f"Sorry, I had trouble processing that request: {str(e)}"
    
    # Save to conversation history if processing succeeded
    if not response_data["speech"].startswith("Sorry, I had trouble"):
        chat_history.append(HumanMessage(content=text))
        chat_history.append(AIMessage(content=response_data["speech"]))
        # Limit global memory to last 10 messages (5 turns) to prevent latency creep
        chat_history = chat_history[-10:]

    return response_data
