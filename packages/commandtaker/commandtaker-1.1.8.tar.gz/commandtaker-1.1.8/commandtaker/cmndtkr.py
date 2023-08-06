import speech_recognition as sr
import pyttsx3

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
print(voices[0].id)
engine.setProperty('voices', voices[0].id)

def speak(audio):
    engine.say(audio)
    print(audio)
    engine.runAndWait()


def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening....")
        r.pause_threshold = 1
        audio = r.listen(source, timeout=1, phrase_time_limit= 5)
    try:
        print("Recognising....")
        query = r.recognize_google(audio, language='en-in')
        print(f"user said:\n {query}")
    except Exception as e:
        return 'none'
    return query


