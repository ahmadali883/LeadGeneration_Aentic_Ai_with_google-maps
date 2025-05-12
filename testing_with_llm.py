import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# --- 1. Configuration ---
load_dotenv()
API_KEY = os.getenv('GOOGLE_API_KEY')

if not API_KEY:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    # Handle the error appropriately, e.g., exit or raise an exception
    exit() # Or raise ValueError("GOOGLE_API_KEY not set.")

genai.configure(api_key=API_KEY)

# --- 2. Define Tool Schemas (Functions the LLM can 'call') ---

# Tool for Google Maps Search
search_Maps_func = {
    "name": "search_Maps",
    "description": "Searches Google Maps for businesses based on a query.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search term for Google Maps (e.g., 'cafes in islamabad', 'restaurants near Eiffel Tower'). Include the type of place and location.",
            },
            "num_results": {
                "type": "integer",
                "description": "Optional. The desired approximate number of business results to find. Defaults to 20 if not specified.",
            },
        },
        "required": ["query"],
    },
}

# Tool for Preparing WhatsApp Message Details
prepare_whatsapp_message_func = {
    "name": "prepare_whatsapp_message",
    "description": "Prepares the content and specifies the number of recipients for a WhatsApp message campaign, typically intended to be sent to leads found via a search.",
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The exact content of the WhatsApp message to be sent.",
            },
            "k": {
                "type": "integer",
                "description": "Optional. The maximum number of recipients (leads) from the search results to send the message to. If omitted, the message might be intended for all found leads or requires clarification.",
            },
             "target_numbers": { # Added for sending direct messages without search
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional. A specific list of phone numbers to send the message to. Use this only if the user explicitly provides numbers and doesn't ask to search.",
            }
        },
        "required": ["message"],
    },
}


# --- 3. Initialize the LLM Model with Tools ---
# Use a model that supports function calling, like Gemini 1.5 Flash or Pro
# Adjust model name if needed (e.g., 'gemini-1.5-pro-latest')
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    tools=[search_Maps_func, prepare_whatsapp_message_func]
)


# --- 4. LLM Interaction Function ---
def get_agent_plan(user_input: str) -> List[Dict[str, Any]]:
    """
    Processes user input using the LLM to determine intent and extract parameters
    for function calls (tools).

    Args:
        user_input: The raw text input from the user.

    Returns:
        A list of dictionaries, where each dictionary represents a function call
        planned by the LLM, containing 'function_name' and 'args'.
        Returns an empty list if no specific function call is identified.
    """
    planned_calls = []
    try:
        # Start a chat session to maintain context if needed, though for single turn it's simple
        chat = model.start_chat()

        # Send the user input to the LLM
        prompt = f"""Analyze the following user request for lead generation. Determine the required actions (search Google Maps, send WhatsApp message, or both). Extract all necessary parameters for the corresponding functions.

        User Request: "{user_input}"

        Based on the request, identify the function(s) to call and the arguments for each. If the user wants to send a message based on search results, first call 'search_Maps' and then 'prepare_whatsapp_message'. If they only want to send a message to specific numbers, only call 'prepare_whatsapp_message' with the 'target_numbers'. If they only want to search, only call 'search_Maps'.
        """
        response = chat.send_message(prompt)

        # --- 5. Parse LLM Response for Function Calls ---
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    call = part.function_call
                    function_name = call.name
                    args = {key: value for key, value in call.args.items()}

                    # Basic validation/Defaults (optional based on schema)
                    if function_name == "search_Maps" and "num_results" not in args:
                         args["num_results"] = 20 # Set default if LLM didn't

                    planned_calls.append({
                        "function_name": function_name,
                        "args": args
                    })
                    print(f"LLM wants to call: {function_name} with args: {args}") # Debug print

        if not planned_calls:
             # Handle cases where the LLM responded with text instead of a function call
             # This might happen if the request is unclear, or purely conversational.
             print("LLM did not suggest a specific function call. Response text:")
             print(response.text)


    except Exception as e:
        print(f"An error occurred during LLM interaction: {e}")
        # Handle exceptions (e.g., API errors, network issues)

    return planned_calls


# --- 6. Example Usage ---
if __name__ == "__main__":
    # Example 1: Search and Message
    request1 = "Find cafes in Islamabad and send the first 5 this message: 'Hello! We have a special offer today.'"
    print(f"\n--- Processing Request 1: '{request1}' ---")
    plan1 = get_agent_plan(request1)
    print("\nExecution Plan 1:")
    print(json.dumps(plan1, indent=2))
    # Expected: Calls to search_Maps and prepare_whatsapp_message

    print("-" * 30)

    # Example 2: Search Only
    request2 = "Show me barber shops in Malakand, maybe 10 of them."
    print(f"\n--- Processing Request 2: '{request2}' ---")
    plan2 = get_agent_plan(request2)
    print("\nExecution Plan 2:")
    print(json.dumps(plan2, indent=2))
    # Expected: Call to search_Maps

    print("-" * 30)

    # Example 3: Message Only (Direct Numbers - Hypothetical User Input)
    request3 = "Send 'Meeting reminder for tomorrow at 10 AM' to +923001234567 and +923339876543"
    print(f"\n--- Processing Request 3: '{request3}' ---")
    plan3 = get_agent_plan(request3)
    print("\nExecution Plan 3:")
    print(json.dumps(plan3, indent=2))
    # Expected: Call to prepare_whatsapp_message with target_numbers

    print("-" * 30)

     # Example 4: Message Only (Using 'k' - Less common without search context, but possible)
    request4 = "Draft a welcome message and prepare to send it to the top 3 leads."
    print(f"\n--- Processing Request 4: '{request4}' ---")
    plan4 = get_agent_plan(request4)
    print("\nExecution Plan 4:")
    print(json.dumps(plan4, indent=2))
    # Expected: Call to prepare_whatsapp_message (message content might be vague here, LLM might ask for clarification or make a guess)

    print("-" * 30)

    # Example 5: Vague request
    request5 = "Tell me about lead generation."
    print(f"\n--- Processing Request 5: '{request5}' ---")
    plan5 = get_agent_plan(request5)
    print("\nExecution Plan 5:")
    print(json.dumps(plan5, indent=2))
    # Expected: Empty plan, LLM text response printed by the function.