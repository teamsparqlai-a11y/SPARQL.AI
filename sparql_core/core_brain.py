import os
from openai import OpenAI
# We no longer need dotenv because we are not using a secret API key
# from dotenv import load_dotenv 
from .memory import MemoryManager
from .tools import TOOL_MANIFEST, call_tool

# We no longer need to load the .env file
# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

class CoreBrain:
    def __init__(self):
        # === THIS IS THE MAIN CHANGE ===
        # We are pointing the OpenAI client to your local Ollama server, which is free.
        self.client = OpenAI(
            base_url='http://localhost:11434/v1', # Points to local Ollama
            api_key='ollama' # Can be any string, 'ollama' is standard
        )
        # === END OF CHANGE ===
        
        self.memory = MemoryManager()

    def get_system_prompt(self) -> str:
        """Builds the master system prompt with memory."""
        
        # This is where you define your AI's core personality from your vision
        base_prompt = (
            "You are SPARQL.AI, a 'Self Thinking Autonomous Real-time eXperience' agent."
            "You are helpful, empathetic, and capable of performing actions."
            "You have access to tools to perform actions and a long-term memory."
            "When a user asks you to remember something, use the 'save_to_memory' tool."
        )
        
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
            model="qwen:4b", # <-- THIS IS THE FIX. Switched to a tool-capable model
            messages=messages_to_send,
            tools=TOOL_MANIFEST,
            tool_choice="auto" # Let the AI decide if it needs a tool
        )
        
        response_message = response.choices[0].message
        
        # 5. Check if the AI wants to call a tool (The "Action Layer")
        if response_message.tool_calls:
            # AI wants to act!
            
            # Add the AI's "intention" to call a tool to history
            conversation_history.append(response_message)
            
            # Execute all tool calls
            for tool_call in response_message.tool_calls:
                tool_result = call_tool(tool_call)
                
                # Add the *result* of the tool call to history
                # This shows the AI what happened
                conversation_history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": tool_result,
                    }
                )
            
            # 6. Call the AI *AGAIN* with the tool results
            # This lets the AI give a natural language summary
            # (e.g., "I've saved your name to memory.")
            
            # Re-build the messages to send, now including the tool results
            messages_to_send = [
                {"role": "system", "content": system_prompt},
            ] + conversation_history

            final_response = self.client.chat.completions.create(
                model="qwen:4b", # <-- THIS MUST MATCH THE MODEL ABOVE
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