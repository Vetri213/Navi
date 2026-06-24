import re
import sounddevice as sd
import numpy as np
import soundfile as sf
import tempfile, os, requests
import platform
import simpleaudio as sa
import pygame


system = platform.system().lower()
if system == "windows":
    sd.default.device = 2

def record_audio(duration=5, samplerate=16000):
    print("🎤 Listening...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()
    print("✅ Recording complete.")
    return np.squeeze(audio)

def transcribe_audio_with_eleven(audio_data, samplerate=16000):
    ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
    url = "https://api.elevenlabs.io/v1/speech-to-text"
    headers = {"xi-api-key": ELEVEN_API_KEY}

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, audio_data, samplerate, subtype="PCM_16")
        with open(tmp.name, "rb") as f:
            files = {"file": (tmp.name, f, "Assets/audio/wav"), "model_id": (None, "scribe_v1")}
            r = requests.post(url, headers=headers, files=files)
    return r.json().get("text", "") if r.status_code == 200 else None

def clean_tts_text(text: str) -> str:
    """
    Cleans AI-generated text for natural speech:
    - Removes Markdown and formatting symbols
    - Strips line-start bullets like '1.' or '2)'
    - Keeps meaningful numbers and words intact
    """
    # Remove Markdown bold/italic symbols
    text = re.sub(r"[*_#>`]+", "", text)

    # Remove step numbers only if they’re at the start of a line
    text = re.sub(r"^\s*\d+[\.\)]\s*", "", text, flags=re.MULTILINE)

    # Remove excessive whitespace or line breaks
    text = re.sub(r"\s+", " ", text).strip()

    # Optional: Capitalize first letter for smoother speech
    if text:
        text = text[0].upper() + text[1:]

    return text


# Initialize pygame mixer once
pygame.mixer.init()

# Global variable to track current playback
current_audio_channel = None

import pygame
import tempfile
import os
import requests
import time
from core.voice_handler import record_audio, transcribe_audio_with_eleven  # to use for post-speech listening

pygame.mixer.init()
current_audio_channel = None

def speak_with_eleven(text, voice_id="gCr8TeSJgJaeaIoV4RWH", on_finished=None):
    """Speak text via ElevenLabs and trigger callback after speech ends."""
    global current_audio_channel

    ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
    if not ELEVEN_API_KEY:
        print("❌ ELEVEN_API_KEY missing in environment.")
        return
    # "[Strong Tamil Accent] [Slowly] [Instructive]"+
    # Clean text
    clean_text = "".join(ch for ch in text if ch.isalnum() or ch.isspace() or ch in ".,!?")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Accept": "audio/mpeg",
        "Content-Type": "application/json"
    }
    #model_id="eleven_multilingual_v2"
    payload = {
        "text": clean_text,
        "model_id" : "eleven_multilingual_v2",
        # "model_id": "eleven_turbo_v2",
        "voice_settings": {"stability": 0.6, "similarity_boost": 0.8}
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print("❌ ElevenLabs error:", response.text)
        return

    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.write(response.content)
    tmp.close()

    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

    try:
        pygame.mixer.music.load(tmp.name)
        pygame.mixer.music.play()
        current_audio_channel = tmp.name

        # Wait for completion (non-blocking)
        def monitor_playback():
            while pygame.mixer.music.get_busy():
                time.sleep(0.2)
            print("🎧 Navi finished speaking.")
            if on_finished:
                on_finished()

        import threading
        threading.Thread(target=monitor_playback, daemon=True).start()

    except Exception as e:
        print("⚠️ Could not play:", e)


def stop_speech():
    """Stop any ongoing speech playback."""
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

def listen_for_yes_no(duration=4):
    """Listen briefly and detect if user said yes or no."""
    print("🎙️ Listening for yes/no...")
    audio = record_audio(duration=duration)
    text = transcribe_audio_with_eleven(audio)
    if not text:
        print("😶 No response detected.")
        return None

    text_lower = text.lower()
    if any(word in text_lower for word in ["yes", "yeah", "yup", "sure", "ok", "okay"]):
        print("✅ Detected 'yes'")
        return "yes"
    elif any(word in text_lower for word in ["no", "nope", "nah", "not really"]):
        print("🚫 Detected 'no'")
        return "no"
    else:
        print(f"🤔 Unclear response: {text}")
        return None

