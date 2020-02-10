# import packages
import speech_recognition as sr

# create Recognizer
r = sr.Recognizer()

# create  Microphone
mic = sr.Microphone()

with mic as source:
    r.adjust_for_ambient_noise(source)
    audio = r.listen(source)

try:
    print(r.recognize_google(audio))
except sr.UnknownValueError:
    print("ERROR: Speech Unrecognizable")
