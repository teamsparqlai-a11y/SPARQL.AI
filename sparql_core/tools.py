import json
import datetime
from .memory import MemoryManager
from googlesearch import search  # <-- Make sure this is imported

# Initialize the memory manager
memory = MemoryManager()

# --- EXISTING TOOLS ---

def get_current_time() -> str:
    """Returns the current date and time."""
    return datetime.datetime.now().isoformat()

def save_to_memory(key: str, value: str) -> str:
    """
    Saves a piece of information to the user's long-term memory.
    
    Args:
        key: The category or name of the fact (e.g., "user_name", "favorite_food").
        value: The information to save (e.g., "Rahul", "Pizza").
    """
    memory.save(key, value)
    return f"Successfully saved {key} = {value} to long-term memory."

def load_from_memory(key: str) -> str:
    """
    Retrieves a piece of information from the user's long-term memory.
    
    Args:
        key: The category or name of the fact to retrieve.
    """
    value = memory.load(key)
    if value:
        return f"Retrieved {key} = {value} from long-term memory."
    return f"No value found for {key} in memory."

# --- NEW TOOL ---

def google_search(query: str) -> str:
    """
    Performs a Google search for the given query and returns the top 3 results.
    Use this for any questions about current events, facts, or real-time information.
    
    Args:
        query: The string to search for on Google (e.g., 'weather in Ghaziabad').
    """
    print(f"[Tool Action: Searching Google for '{query}']")
    try:
        # Get the first 3 results
        results = []
        # The search() function is a generator, so we loop 3 times
        for result in search(query, num_results=3, advanced=True):
            results.append(f"Title: {result.title}\nDescription: {result.description}\nURL: {result.url}\n")
        
        if not results:
            return "No search results found."
            
        return "\n".join(results)
    
    except Exception as e:
        print(f"[Search Error]: {e}")
        return f"An error occurred during the search: {e}"

# --- UPDATED MANIFEST AND DICTIONARY ---

# This "manifest" tells the AI which tools it has
TOOL_MANIFEST = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returns the current date and time.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_to_memory",
            "description": "Saves a fact to the user's long-term memory. Use this when the user says 'remember my name is...' or 'my favorite color is...'",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "The key or category of the fact to save."},
                    "value": {"type": "string", "description": "The value of the fact to save."},
                },
                "required": ["key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "load_from_memory",
            "description": "Loads a specific fact from the user's long-term memory. Use this when the user asks 'what is my name?'",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "The key or category of the fact to load."},
                },
                "required": ["key"],
            },
        },
    },
    # --- ADDING THE NEW TOOL TO THE MANIFEST ---
    {
        "type": "function",
        "function": {
            "name": "google_search",
            "description": "Performs a Google search for a given query. Use this to find real-time information, weather, news, facts, or anything you don't know.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query (e.g., 'weather in Ghaziabad', 'latest tech news')."},
                },
                "required": ["query"],
            },
        },
    },
]

# This dictionary maps tool names to their actual Python functions
AVAILABLE_TOOLS = {
    "get_current_time": get_current_time,
    "save_to_memory": save_to_memory,
    "load_from_memory": load_from_memory,
    "google_search": google_search  # <-- ADDING THE NEW TOOL HERE
}

def call_tool(tool_call):
    """Executes a tool call requested by the AI."""
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)
    
    if func_name in AVAILABLE_TOOLS:
        function_to_call = AVAILABLE_TOOLS[func_name]
        
        # This logic routes the arguments to the correct function
        if func_name == "save_to_memory":
            result = function_to_call(key=func_args.get("key"), value=func_args.get("value"))
        elif func_name == "load_from_memory":
            result = function_to_call(key=func_args.get("key"))
        elif func_name == "google_search":
            result = function_to_call(query=func_args.get("query"))
        else: # For get_current_time
            result = function_to_call() 
            
        return result
    else:
        return f"Error: Tool '{func_name}' not found."