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

def speak_with_eleven(text, voice_id="JBFqnCBsd6RMkjVDRZzb"):
    """Convert text to speech using ElevenLabs API and play it with pygame."""
    global current_audio_channel

    ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
    if not ELEVEN_API_KEY:
        print("❌ ELEVEN_API_KEY missing in environment.")
        return

    # --- Clean the text (remove unwanted chars like * but keep numbers) ---
    clean_text = "".join(ch for ch in text if ch.isalnum() or ch.isspace() or ch in ".,!?")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Accept": "audio/mpeg",
        "Content-Type": "application/json"
    }
    payload = {
        "text": clean_text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {"stability": 0.6, "similarity_boost": 0.8}
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print("❌ Error from ElevenLabs:", e)
        return

    # Save to temporary MP3 file
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.write(response.content)
    tmp.close()

    # Stop any previous playback first
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

    # Play new audio
    try:
        pygame.mixer.music.load(tmp.name)
        pygame.mixer.music.play()
        current_audio_channel = tmp.name
    except Exception as e:
        print("⚠️ Failed to play audio:", e)

def stop_speech():
    """Stop any ongoing speech playback."""
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

