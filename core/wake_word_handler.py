# Example placeholder using SpeechRecognition
import speech_recognition as sr
import threading

def listen_for_wake_word(callback):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    def loop():
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("🎧 Listening for 'Hey Navi'...")
            while True:
                audio = recognizer.listen(source)
                try:
                    text = recognizer.recognize_google(audio).lower()
                    if "hey navi" in text:
                        print("👂 Wake word detected.")
                        callback()
                except sr.UnknownValueError:
                    pass

    threading.Thread(target=loop, daemon=True).start()
