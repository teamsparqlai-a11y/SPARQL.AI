import speech_recognition as sr
import pyttsx3

class VoiceInterface:
    def __init__(self):
        # Initialize the recognizer
        self.recognizer = sr.Recognizer()
        
        # --- CHANGE 1: REMOVED THE TTS INIT ---
        # We will now initialize it inside the speak() function
        # self.tts_engine = pyttsx3.init() 
        
        # We will manually set the energy threshold instead of dynamic
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 300  # We'll keep this sensitive setting

    def listen_for_command(self) -> str:
        """
        Listens for audio from the microphone and returns it as text.
        Returns None if there is an error.
        """
        text = None
        try:
            # We are using the system's default mic (no device_index)
            with sr.Microphone() as source:
            
                # Listen for a second to get a good noise baseline
                self.recognizer.adjust_for_ambient_noise(source, duration=1) 
                print("Listening... (speak now)")
                
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=7, phrase_time_limit=10)
                
                # Recognize speech using Google's ONLINE recognizer
                print("Recognizing...")
                # --- CHANGE 2: ADD LANGUAGE HINT (see notes below) ---
                # Let's add English (India) and Hindi as options for Google to check
                text = self.recognizer.recognize_google(audio, language="en-IN")
        
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Google Speech Recognition request failed; {e}")
        except sr.WaitTimeoutError:
            print("Listening timed out... please speak sooner.")
        except Exception as e:
            print(f"An unexpected error occurred during listening: {e}")
            
        return text

    def speak(self, text: str):
        """
        Speaks the given text out loud.
        """
        if text:
            print(f"SPARQL.AI: {text}")
            try:
                # --- CHANGE 3: INITIALIZE AND RUN TTS INSIDE THE FUNCTION ---
                # This is the fix for the "only speaks once" problem.
                tts_engine = pyttsx3.init()
                tts_engine.say(text)
                tts_engine.runAndWait()
                tts_engine.stop() # Ensure it stops cleanly
            except Exception as e:
                print(f"[ERROR] Could not speak text: {e}")