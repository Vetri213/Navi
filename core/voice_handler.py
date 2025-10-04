import sounddevice as sd
import numpy as np
import soundfile as sf
import tempfile, os, requests

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
            files = {"file": (tmp.name, f, "audio/wav"), "model_id": (None, "scribe_v1")}
            r = requests.post(url, headers=headers, files=files)
    return r.json().get("text", "") if r.status_code == 200 else None
