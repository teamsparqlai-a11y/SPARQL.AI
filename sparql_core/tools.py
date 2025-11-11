import json
from .memory import MemoryManager

# Initialize the memory manager
memory = MemoryManager()

def get_current_time() -> str:
    """Returns the current date and time."""
    import datetime
    return datetime.datetime.now().isoformat()

def save_to_memory(key: str, value: str) -> str:
    """
    Saves a piece of information to the user's long-term memory.
    Use this to remember facts about the user, their preferences, etc.
    
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

# This is the "manifest" of all available tools for the AI
# We will pass this to the AI so it knows what it can do
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
            "description": "Saves a fact to the user's long-term memory.",
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
            "description": "Loads a specific fact from the user's long-term memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "The key or category of the fact to load."},
                },
                "required": ["key"],
            },
        },
    },
]

# This dictionary maps tool names to their actual Python functions
AVAILABLE_TOOLS = {
    "get_current_time": get_current_time,
    "save_to_memory": save_to_memory,
    "load_from_memory": load_from_memory,
}

def call_tool(tool_call):
    """Executes a tool call requested by the AI."""
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)
    
    if func_name in AVAILABLE_TOOLS:
        function_to_call = AVAILABLE_TOOLS[func_name]
        
        # Call the function with arguments
        if func_name == "save_to_memory":
            result = function_to_call(key=func_args.get("key"), value=func_args.get("value"))
        elif func_name == "load_from_memory":
            result = function_to_call(key=func_args.get("key"))
        else:
            result = function_to_call() # For functions with no args, like get_current_time
            
        return result
    else:
        return f"Error: Tool '{func_name}' not found."