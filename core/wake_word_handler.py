
import os
import platform
import threading
import queue
import struct
import pvporcupine
import pyaudio


def get_wake_word_model_path():
    """Get the appropriate wake word model path based on platform."""
    system = platform.system().lower()
    
    # Determine the platform-specific model filename
    if system == "darwin":  # macOS
        model_filename = "Hey-Navi_en_mac_v3_0_0.ppn"
        model_dir = "Hey-Navi_en_mac_v3_0_0"
    elif system == "windows":
        model_filename = "Hey-Navi_en_windows_v3_0_0.ppn"
        model_dir = "Hey-Navi_en_windows_v3_0_0"
    elif system == "linux":
        model_filename = "Hey-Navi_en_linux_v3_0_0.ppn"
        model_dir = "Hey-Navi_en_linux_v3_0_0"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")
    
    # Try multiple possible paths
    possible_paths = [
        os.path.join(model_dir, model_filename),  # In subdirectory
        model_filename,  # In current directory
        os.path.join(os.path.dirname(__file__), model_dir, model_filename),  # Relative to script
        os.path.join(os.path.dirname(__file__), model_filename)  # Relative to script
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found wake word model: {path}")
            return path
    
    # If not found, return None and warn user
    print(f"⚠️ Wake word model not found for {system}.")
    print(f"Expected one of: {possible_paths}")
    print(f"\n📋 To add Windows/Linux support:")
    print(f"   1. Go to https://console.picovoice.ai/")
    print(f"   2. Create 'Hey Navi' wake word for your platform")
    print(f"   3. Download and place in project directory")
    return None


def wake_word_listener(wake_event_queue, access_key, model_path):
    """
    Background thread function that listens for the wake word.
    When detected, it puts a signal in the queue to notify the main thread.
    
    Args:
        wake_event_queue: Queue to send wake word detection events
        access_key: Picovoice API access key
        model_path: Path to the .ppn wake word model file
    """
    porcupine = None
    pa = None
    audio_stream = None
    
    try:
        # Initialize Porcupine
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[model_path]
        )
        
        # Set up PyAudio
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        
        print("🎧 Wake word detection active. Say 'Hey Navi' to activate...")
        
        while True:
            # Read audio frame
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            
            # Process audio frame
            keyword_index = porcupine.process(pcm)
            
            # If wake word detected
            if keyword_index >= 0:
                print("✨ 'Hey Navi' detected!")
                # Send signal to main thread
                wake_event_queue.put("WAKE_WORD_DETECTED")
                
    except Exception as e:
        print(f"❌ Wake word listener error: {e}")
    finally:
        # Clean up resources
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if porcupine is not None:
            porcupine.delete()


class WakeWordDetector:
    """
    Wake word detector that can be integrated into a GUI application.
    Runs the detection in a background thread and provides a queue for event notifications.
    """
    
    def __init__(self, access_key):
        """
        Initialize the wake word detector.
        
        Args:
            access_key: Picovoice API access key
        """
        self.access_key = access_key
        self.wake_event_queue = queue.Queue()
        self.listener_thread = None
        self.is_running = False
        
    def start(self):
        """Start the wake word detection in a background thread."""
        if self.is_running:
            print("⚠️ Wake word detection is already running")
            return False
            
        try:
            # Get the platform-specific model path
            model_path = get_wake_word_model_path()
            if not model_path:
                print("⚠️ Wake word model not found. Wake word detection disabled.")
                return False
            
            # Start the listener thread (daemon so it exits when main program exits)
            self.listener_thread = threading.Thread(
                target=wake_word_listener,
                args=(self.wake_event_queue, self.access_key, model_path),
                daemon=True
            )
            self.listener_thread.start()
            self.is_running = True
            print("✅ Wake word detection started successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start wake word detection: {e}")
            return False
    
    def check_for_wake_word(self):
        """
        Check if wake word was detected (non-blocking).
        
        Returns:
            bool: True if wake word was detected, False otherwise
        """
        try:
            event = self.wake_event_queue.get_nowait()
            if event == "WAKE_WORD_DETECTED":
                return True
        except queue.Empty:
            pass
        return False

