# Architecture Overview

Technical documentation for developers and contributors.

---

##  System Architecture

### High-Level Overview

```

                     User Interface                       
              (CustomTkinter - navi_assistant.py)        

                 
    
                             
        
   Voice              Screenshot 
  Handler              Handler   
        
                            
        
        

   Gemini    
   Handler   

```

---

##  Project Structure

```
Navi/
 main.py                          # Application entry point
 core/                            # Core functionality modules
    gemini_handler.py           # Google Gemini AI integration
    voice_handler.py            # Speech recognition & synthesis
    screenshot_handler.py       # Screen capture functionality
    wake_word_handler.py        # Wake word detection
 UI/                              # User interface components
    navi_assistant.py           # Main UI class
 Hey-Navi_en_mac_v3_0_0/         # Wake word model
    Hey-Navi_en_mac_v3_0_0.ppn # Picovoice model file
 requirements.txt                 # Python dependencies
 .env                            # Environment variables (not in repo)
 .gitignore                      # Git ignore rules
 README.md                       # Project documentation
```

---

##  Core Components

### 1. Main Application (`main.py`)

**Purpose:** Application entry point and initialization

**Key Functions:**
```python
if __name__ == "__main__":
    configure_gemini()      # Initialize Gemini AI
    app = NaviAssistant()   # Create UI instance
    app.mainloop()          # Start event loop
```

**Flow:**
1. Load environment variables
2. Configure Gemini API
3. Initialize UI
4. Start CustomTkinter main loop

---

### 2. Gemini Handler (`core/gemini_handler.py`)

**Purpose:** Interface with Google Gemini AI for vision and language understanding

**Key Functions:**

#### `configure_gemini()`
```python
def configure_gemini():
    """Initialize Gemini with API key from environment"""
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
```

#### `query_gemini(user_instruction, screenshot_image)`
```python
def query_gemini(user_instruction, screenshot_image):
    """
    Send user request and screenshot to Gemini
    Returns: Step-by-step instructions as text
    """
    # Convert screenshot to bytes
    # Create prompt with context
    # Call Gemini 2.0 Flash model
    # Return response
```

#### `parse_steps(response_text)`
```python
def parse_steps(response_text):
    """
    Parse Gemini response into numbered steps
    Returns: List of instruction strings
    """
    # Extract numbered steps
    # Return as list
```

**AI Model:** `gemini-2.0-flash-exp`
- Multimodal (vision + text)
- Fast response times
- Context-aware understanding

---

### 3. Voice Handler (`core/voice_handler.py`)

**Purpose:** Manage all voice-related functionality

**Key Functions:**

#### `record_audio(duration=5, samplerate=16000)`
```python
def record_audio(duration=5, samplerate=16000):
    """
    Record audio from microphone
    Returns: NumPy array of audio data
    """
    # Use sounddevice to capture audio
    # Return audio array
```

#### `transcribe_audio_with_eleven(audio_data, samplerate=16000)`
```python
def transcribe_audio_with_eleven(audio_data, samplerate=16000):
    """
    Convert speech to text using ElevenLabs
    Returns: Transcribed text string
    """
    # Save audio to temporary WAV file
    # Send to ElevenLabs API
    # Return transcribed text
```

#### `speak_with_eleven(text, voice_id, on_finished=None)`
```python
def speak_with_eleven(text, voice_id="JBFqnCBsd6RMkjVDRZzb", on_finished=None):
    """
    Convert text to speech and play
    Calls on_finished callback when complete
    """
    # Clean text for speech
    # Call ElevenLabs TTS API
    # Play audio with pygame
    # Monitor playback in separate thread
    # Call on_finished when done
```

#### `listen_for_yes_no(duration=4)`
```python
def listen_for_yes_no(duration=4):
    """
    Listen for yes/no response
    Returns: "yes", "no", or None
    """
    # Record audio
    # Transcribe
    # Detect yes/no keywords
    # Return result
```

**Audio Processing:**
- **Input:** sounddevice (16kHz, mono, int16)
- **Output:** pygame mixer (MP3 playback)
- **Format:** WAV for API transmission

---

### 4. Screenshot Handler (`core/screenshot_handler.py`)

**Purpose:** Capture screen content while hiding UI

**Key Functions:**

#### `take_screenshot(window)`
```python
def take_screenshot(window):
    """
    Hide window, capture screen, restore window
    Returns: PIL Image object
    """
    # Hide window (withdraw)
    # Wait for window to disappear
    # Capture screenshot with pyautogui
    # Restore window (deiconify)
    # Return image
```

**Process:**
1. `window.withdraw()` - Hide Tkinter window
2. `time.sleep(0.5)` - Wait for UI to disappear
3. `pyautogui.screenshot()` - Capture screen
4. `window.deiconify()` - Restore window

---

### 5. Wake Word Handler (`core/wake_word_handler.py`)

**Purpose:** Detect "Hey Navi" wake word using Picovoice Porcupine

**Key Class:**

#### `WakeWordDetector`
```python
class WakeWordDetector:
    def __init__(self, access_key):
        """Initialize Porcupine with access key"""
        
    def start(self):
        """Start wake word detection in background thread"""
        
    def check_for_wake_word(self):
        """Check if wake word was detected"""
        
    def stop(self):
        """Stop detection and cleanup"""
```

**Implementation:**
- Runs in separate thread
- Continuously processes audio
- Uses queue for thread-safe communication
- Minimal CPU usage when idle

---

### 6. UI Component (`UI/navi_assistant.py`)

**Purpose:** Main user interface using CustomTkinter

**Key Class:**

#### `NaviAssistant(ctk.CTk)`

**State Management:**
```python
self.is_expanded = False        # UI state
self.steps = []                 # Current instruction steps
self.current_step = 0           # Progress tracker
self.last_screenshot = None     # Cached screenshot
```

**Key Methods:**

##### `expand()`
```python
def expand(self):
    """Expand from button to full panel"""
    # Hide collapsed button
    # Show expanded panel
    # Position window
```

##### `collapse()`
```python
def collapse(self):
    """Collapse to floating button"""
    # Hide expanded panel
    # Show collapsed button
```

##### `voice_input()`
```python
def voice_input(self):
    """Capture and process voice input"""
    # Record audio
    # Transcribe with ElevenLabs
    # Fill input field
    # Process command
```

##### `process_command()`
```python
def process_command(self):
    """Process user request"""
    # Get user text
    # Take screenshot
    # Query Gemini
    # Parse steps
    # Display first step
```

##### `display_step()`
```python
def display_step(self):
    """Show current step with context-aware question"""
    # Get current step
    # Determine follow-up question
    # Update UI
    # Speak instruction
```

##### `handle_yes()` / `handle_no()`
```python
def handle_yes(self):
    """Move to next step"""
    
def handle_no(self):
    """Request clarification"""
```

---

##  Application Flow

### Startup Sequence

```
1. Load .env file
   ↓
2. Configure Gemini API
   ↓
3. Initialize CustomTkinter app
   ↓
4. Create collapsed button UI
   ↓
5. Start wake word detection thread
   ↓
6. Enter main event loop
```

### User Interaction Flow

```
1. User says "Hey Navi"
   ↓
2. Wake word detected
   ↓
3. UI expands
   ↓
4. Start voice recording
   ↓
5. Transcribe speech to text
   ↓
6. Hide UI window
   ↓
7. Capture screenshot
   ↓
8. Show UI window
   ↓
9. Send to Gemini (text + image)
   ↓
10. Parse response into steps
   ↓
11. Display step 1
   ↓
12. Speak instruction
   ↓
13. Listen for yes/no
   ↓
14. If yes: next step (goto 11)
    If no: clarify (goto 9 with clarification prompt)
```

---

##  Threading Model

### Main Thread
- CustomTkinter UI event loop
- User interactions
- UI updates

### Background Threads

1. **Wake Word Detection Thread**
   - Continuously listens for "Hey Navi"
   - Minimal CPU usage
   - Communicates via queue

2. **Voice Recording Thread**
   - Records audio asynchronously
   - Prevents UI blocking
   - Returns via callback

3. **TTS Playback Monitor Thread**
   - Monitors pygame audio playback
   - Triggers yes/no listening when done
   - Daemon thread (auto-cleanup)

**Thread Safety:**
- Queue for wake word communication
- Callbacks for async operations
- No shared mutable state

---

##  API Integrations

### Google Gemini API

**Endpoint:** `generativelanguage.googleapis.com`

**Request:**
```python
{
    "prompt": "User request: [text]",
    "image": {
        "mime_type": "image/png",
        "data": [base64_encoded_screenshot]
    }
}
```

**Response:**
```python
{
    "text": "1. First step\n2. Second step\n3. Third step"
}
```

### ElevenLabs API

**Speech-to-Text Endpoint:** `/v1/speech-to-text`

**Request:**
```python
files = {
    "file": (filename, audio_file, "audio/wav"),
    "model_id": (None, "scribe_v1")
}
headers = {"xi-api-key": API_KEY}
```

**Response:**
```python
{
    "text": "transcribed text",
    "language_code": "eng",
    "words": [...]
}
```

**Text-to-Speech Endpoint:** `/v1/text-to-speech/{voice_id}`

**Request:**
```python
{
    "text": "Text to speak",
    "model_id": "eleven_turbo_v2",
    "voice_settings": {
        "stability": 0.6,
        "similarity_boost": 0.8
    }
}
```

**Response:** Audio stream (MP3)

### Picovoice Porcupine

**Local Processing:** No API calls, runs on-device

**Model:** Custom "Hey Navi" wake word
- File: `Hey-Navi_en_mac_v3_0_0.ppn`
- Platform: macOS (separate models for Windows/Linux)
- Sensitivity: Configurable

---

##  Data Flow

### Voice Input → AI Response

```
Microphone
    ↓ (audio samples)
sounddevice
    ↓ (NumPy array)
WAV file
    ↓ (HTTP POST)
ElevenLabs API
    ↓ (JSON)
Text string
    ↓
Screenshot
    ↓ (PIL Image)
PNG bytes
    ↓ (HTTP POST)
Gemini API
    ↓ (JSON)
Instruction steps
    ↓
UI Display
    ↓
ElevenLabs TTS
    ↓ (MP3 stream)
pygame mixer
    ↓ (audio output)
Speakers
```

---

##  Security Considerations

### API Key Storage
- Stored in `.env` file (not in Git)
- Loaded at runtime
- Never logged or displayed

### Data Privacy
- Screenshots processed in memory
- Not stored permanently
- Sent to Google/ElevenLabs APIs
- Subject to their privacy policies

### Network Security
- HTTPS for all API calls
- No local storage of sensitive data
- API keys never transmitted in logs

---

##  Performance Optimization

### Caching
- Screenshot cached during session
- Wake word model loaded once
- Gemini model reused

### Async Operations
- Voice recording: non-blocking
- API calls: threaded
- TTS playback: background thread

### Resource Management
- Audio buffers: released after use
- Temporary files: auto-deleted
- Threads: daemon mode for cleanup

---

##  Testing Strategy

### Unit Tests
- Individual function testing
- Mock API responses
- Edge case handling

### Integration Tests
- Full flow testing
- API integration verification
- Error handling

### Manual Testing
- Voice recognition accuracy
- UI responsiveness
- Cross-platform compatibility

---

##  Configuration

### Environment Variables

```env
GEMINI_API_KEY=...          # Required
ELEVEN_API_KEY=...          # Required
PICOVOICE_ACCESS_KEY=...    # Required
```

### Hardcoded Constants

**Voice Settings:**
```python
RECORDING_DURATION = 5      # seconds
SAMPLE_RATE = 16000         # Hz
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # ElevenLabs voice
```

**UI Settings:**
```python
COLLAPSED_SIZE = (180, 56)
EXPANDED_SIZE = (420, 600)
POSITION_OFFSET = (100, 130)  # from screen edge
```

---

##  Dependencies

### Core Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| `customtkinter` | Latest | Modern UI framework |
| `google-generativeai` | Latest | Gemini AI SDK |
| `elevenlabs` | Latest | Voice services |
| `pvporcupine` | Latest | Wake word detection |
| `pyautogui` | Latest | Screenshot capture |
| `pygame` | 2.6+ | Audio playback |
| `sounddevice` | Latest | Audio recording |
| `numpy` | Latest | Audio processing |
| `python-dotenv` | Latest | Environment variables |
| `Pillow` | Latest | Image processing |

---

##  Future Architecture Improvements

### Planned Enhancements

1. **Plugin System**
   - Modular command handlers
   - Custom wake words
   - Third-party integrations

2. **Local AI Option**
   - Offline mode
   - Privacy-focused alternative
   - Reduced API costs

3. **Multi-Platform UI**
   - Native mobile apps
   - Web interface
   - Cross-platform consistency

4. **Advanced Caching**
   - Response caching
   - Predictive loading
   - Reduced latency

---

##  Related Documentation

- **[Contributing Guide](Contributing-Guide.md)** - How to contribute
- **[API Reference](API-Reference.md)** - Detailed API docs
- **[Configuration Options](Configuration-Options.md)** - Advanced settings

---

**For Developers:** This architecture is designed to be modular and extensible. Each component can be modified or replaced independently. 
