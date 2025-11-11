import os
from openai import OpenAI
from .memory import MemoryManager
from .tools import TOOL_MANIFEST, call_tool 
import sys 

# --- ROBUST, PERMANENT FIX FOR ENVIRONMENT INJECTION ERRORS ---

# 1. Define all known arguments that the modern OpenAI client accepts.
# We will ONLY pass arguments that are explicitly accepted by the library.
# This prevents Windows environment variables like 'ALLUSERSPROFILE' from causing a crash.
ACCEPTED_KWARGS = [
    'base_url', 'api_key', 'organization', 'project', 'timeout', 'max_retries', 
    'default_headers', 'client', 'transport', 'proxies', 'http_proxy', 'https_proxy'
]

# 2. Capture all environment variables
kwargs = {k.lower(): v for k, v in os.environ.items()}

# 3. Filter environment variables, keeping only ACCEPTED_KWARGS
safe_kwargs = {k: v for k, v in kwargs.items() if k in ACCEPTED_KWARGS}

class CoreBrain:
    def __init__(self):
        
        # Add the necessary Ollama parameters to the safe arguments, overriding any system settings
        safe_kwargs['base_url'] = 'http://localhost:11434/v1' 
        safe_kwargs['api_key'] = 'ollama'
        
        # Initialize the client using ONLY the safe arguments
        try:
             self.client = OpenAI(**safe_kwargs)
        except Exception as e:
            print(f"\n[FATAL ERROR]: Could not initialize OpenAI client. Underlying error: {e}")
            print("Action: Check if the Ollama service is running and accessible.")
            sys.exit(1)
        
        self.memory = MemoryManager()

    def get_system_prompt(self) -> str:
        """Builds the master system prompt with memory."""
        
        # --- PROMPT UPDATED HERE ---
        base_prompt = (
            "You are SPARQL.AI, a 'Self Thinking Autonomous Real-time eXperience' agent."
            "You are helpful, empathetic, and capable of performing actions."
            "You have access to tools to perform actions and a long-term memory."
            "When a user asks to remember something, use the 'save_to_memory' tool."
            "If you are asked for real-time information, news, weather, or facts you don't know, you MUST use the 'google_search' tool."
            "Do not apologize for not having real-time information. Instead, use the 'google_search' tool to find it."
        )
        # --- END OF PROMPT UPDATE ---
        
        # This is your "Personalization Layer v1"
        memory_data = self.memory.get_all_memory_as_string()
        personalized_prompt = f"""
        {base_prompt}

        ---
        Here is what you know about the user (your long-term memory):
        {memory_data}
        ---
        """
        return personalized_prompt

    def chat(self, user_input: str, conversation_history: list):
        """
        Main chat function.
        It orchestrates the LLM, Tools, and Memory.
        """
        
        # 1. Add the user's new message to the history
        conversation_history.append({"role": "user", "content": user_input})
        
        # 2. Create the system prompt (with memory)
        system_prompt = self.get_system_prompt()
        
        # 3. Build the full list of messages to send
        messages_to_send = [
            {"role": "system", "content": system_prompt},
        ] + conversation_history
        
        # 4. Call the AI
        response = self.client.chat.completions.create(
            model="llama3-groq-tool-use:8b", # Using the correct tool-use model.
            messages=messages_to_send,
            tools=TOOL_MANIFEST, # Sending the NEW tool list
            tool_choice="auto" 
        )
        
        response_message = response.choices[0].message
        
        # 5. Check if the AI wants to call a tool (The "Action Layer")
        if response_message.tool_calls:
            conversation_history.append(response_message)
            
            for tool_call in response_message.tool_calls:
                tool_result = call_tool(tool_call)
                
                conversation_history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": tool_result,
                    }
                )
            
            # 6. Call the AI *AGAIN* with the tool results
            messages_to_send = [
                {"role": "system", "content": system_prompt},
            ] + conversation_history

            final_response = self.client.chat.completions.create(
                model="llama3-groq-tool-use:8b", # Using the correct tool-use model.
                messages=messages_to_send
            )
            
            final_message = final_response.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": final_message})
            return final_message
        
        else:
            # No tool needed, just a simple chat response
            chat_response = response_message.content
            conversation_history.append({"role": "assistant", "content": chat_response})
            return chat_response