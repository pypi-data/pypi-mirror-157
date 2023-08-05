from speak import *

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('listening...')
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("recognizing...")
        query = r.recognize_google(audio, language="en-in")
        print(f"aaqa said: {query}")

    except Exception as e:
        print("say that again please...")
        return "none"
    return query
