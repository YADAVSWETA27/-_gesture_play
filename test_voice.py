import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 170)  # Speaking speed
engine.setProperty('volume', 1.0)  # Max volume

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Try changing index if no sound

engine.say("Hello, this is a voice test.")
engine.runAndWait()
