from .core_brain import CoreBrain

def run_sparql_ai():
    print("🚀 SPARQL.AI v0.1 (Core Brain) is online.")
    print("Type 'exit' to end the session.")
    print("-" * 30)
    
    brain = CoreBrain()
    
    # This is your "Short-term Memory"
    conversation_history = [] 

    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'exit':
            print("\nSPARQL.AI: Goodbye! Shutting down.")
            break
            
        try:
            # Get the response from the brain
            response = brain.chat(user_input, conversation_history)
            print(f"\nSPARQL.AI: {response}\n")
        
        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")
            print("Restarting conversation history...")
            conversation_history = [] # Reset history on error

if __name__ == "__main__":
    run_sparql_ai()