from .core_brain import CoreBrain
from .voice_interface import VoiceInterface

def run_sparql_ai():
    print("🚀 SPARQL.AI v0.2 (Voice Edition) is online.")
    print("Say 'exit' to end the session.")
    print("-" * 30)
    
    brain = CoreBrain()
    voice = VoiceInterface()
    
    conversation_history = [] 

    while True:
        try:
            # 1. Listen for your voice
            user_input = voice.listen_for_command()

            if user_input:
                print(f"You: {user_input}")
                
                # 2. Check for the exit command
                if user_input.lower() == 'exit':
                    voice.speak("Goodbye! Shutting down.")
                    break
                
                # 3. Get response from the brain
                response = brain.chat(user_input, conversation_history)
                
                # 4. Speak the response
                voice.speak(response)
            
            else:
                pass 
        
        except Exception as e:
            print(f"\n[ERROR] An unexpected error occurred: {e}")
            voice.speak("An error occurred. Restarting the conversation.")
            conversation_history = []
            
if __name__ == "__main__":
    run_sparql_ai()