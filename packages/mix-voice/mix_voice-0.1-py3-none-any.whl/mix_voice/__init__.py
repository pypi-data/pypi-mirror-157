# Imports modules
import speech_recognition as sr # helps to recognize the audio
import pyttsx3
import datetime

# Creating an engine for voice
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')

# Voice class - decides the character of the voice
class Voice:
    def male():
        engine.setProperty('voice', voices[0].id)
    def female():
        engine.setProperty('voice', voices[1].id)

# Defines the speak function which will help The AI to speak
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def wish():
    hour = int(datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good morning")
    elif hour >= 4 and hour < 9:
        engine.setProperty('rate', 100)
        speak("Good morning. You have disturbed me, I was in my sleep. There was a beautiful dream in my sleep...")
        engine.setProperty('rate', 200)
        speak("Anyways, tell how may I help you...")
    elif hour >= 12 and hour < 18:
        speak("Good afternoon")
    else:
        speak("Good evening")

# Takes the commands of the user
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"You said: {query}\n")
    except Exception as e:
        # print(e)
        print("Say that again please")
        return "None"
    return query