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

def speak_with_eleven(text, voice_id="JBFqnCBsd6RMkjVDRZzb"):
    """
    Convert text to speech using ElevenLabs API and play it with pygame.
    Non-blocking playback — Navi can talk while doing other stuff.
    """
    ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
    if not ELEVEN_API_KEY:
        raise RuntimeError("ELEVEN_API_KEY not found in environment variables.")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"  # ask for MP3
    }

    text = clean_tts_text(text)

    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.8
        }
    }

    # Request audio
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: {response.text}")
        return None

    # Save MP3 file temporarily
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.write(response.content)
    tmp.flush()
    tmp.close()

    # Initialize pygame if not already
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    try:
        # Load and play
        pygame.mixer.music.load(tmp.name)
        pygame.mixer.music.play()
        print(f"🔊 Navi speaking: “{text}”")

        # Optional: block until playback finishes
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"⚠️ Playback failed: {e}")
        return None

    finally:
        # Clean up
        try:
            os.remove(tmp.name)
        except OSError:
            pass

    return True