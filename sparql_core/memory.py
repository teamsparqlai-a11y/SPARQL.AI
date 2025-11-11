import json
import os

class MemoryManager:
    def __init__(self, memory_file="long_term_memory.json"):
        self.memory_file = memory_file
        self._ensure_memory_file_exists()

    def _ensure_memory_file_exists(self):
        """Creates the memory file if it doesn't exist."""
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w') as f:
                json.dump({}, f)

    def _load_all(self) -> dict:
        """Loads the entire memory dictionary from the file."""
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save(self, key: str, value: any):
        """Saves a single key-value pair to memory."""
        memory_data = self._load_all()
        memory_data[key] = value
        with open(self.memory_file, 'w') as f:
            json.dump(memory_data, f, indent=4)

    def load(self, key: str) -> any:
        """Loads a single value by its key."""
        memory_data = self._load_all()
        return memory_data.get(key)
    
    def get_all_memory_as_string(self) -> str:
        """Returns the entire memory as a formatted string."""
        memory_data = self._load_all()
        if not memory_data:
            return "No long-term memories found."
        
        # Format as a simple string for the AI prompt
        return "\n".join([f"- {key}: {value}" for key, value in memory_data.items()])