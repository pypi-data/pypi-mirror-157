from speak import *


def wishMe():
    time = datetime.datetime.now().hour
    if time>=0 and time<=12:
        speak("Good Morning Sir!")
    elif time>=12 and time<=16:
        speak("Good Afternoon Sir!")
    else:
        speak("Good Afternoon Sir!")