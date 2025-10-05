# Installation Guide

This comprehensive guide will walk you through installing Navi on your system.

---

##  System Requirements

### Minimum Requirements
- **Operating System:** Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python:** Version 3.13 or higher
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 500MB free space
- **Internet:** Stable broadband connection
- **Microphone:** Built-in or external microphone
- **Speakers/Headphones:** For audio output

### Recommended Specifications
- **RAM:** 16GB for optimal performance
- **Internet:** 10 Mbps or faster
- **Microphone:** High-quality USB microphone for better voice recognition

---

##  Step-by-Step Installation

### Step 1: Install Python

#### Windows
1. Download Python 3.13+ from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important:** Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   ```bash
   python --version
   ```

#### macOS
1. Install Homebrew (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```bash
   brew install python@3.13
   ```
3. Verify installation:
   ```bash
   python3 --version
   ```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.13 python3-pip
python3 --version
```

---

### Step 2: Clone the Repository

#### Using Git (Recommended)
```bash
git clone https://github.com/Vetri213/Navi.git
cd Navi
```

#### Download ZIP
1. Go to [GitHub Repository](https://github.com/Vetri213/Navi)
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Open terminal/command prompt in the extracted folder

---

### Step 3: Create Virtual Environment (Recommended)

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `customtkinter` - Modern UI framework
- `google-generativeai` - Gemini AI integration
- `elevenlabs` - Voice synthesis and recognition
- `pvporcupine` - Wake word detection
- `pyautogui` - Screen capture
- `pygame` - Audio playback
- `sounddevice` - Audio recording
- `numpy` - Numerical operations
- `soundfile` - Audio file handling
- `python-dotenv` - Environment variable management
- `Pillow` - Image processing

---

### Step 5: Configure API Keys

1. Create a `.env` file in the project root:
   ```bash
   touch .env
   ```

2. Open `.env` in a text editor and add:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ELEVEN_API_KEY=your_elevenlabs_api_key_here
   PICOVOICE_ACCESS_KEY=your_picovoice_access_key_here
   ```

3. Replace the placeholder values with your actual API keys

 **Need help getting API keys?** See the [API Keys Setup Guide](API-Keys-Setup.md)

---

### Step 6: Verify Installation

Run the following command to test your installation:

```bash
python main.py
```

You should see:
```
 Loading .env from: /path/to/.env
 ELEVEN_API_KEY loaded: Yes
pygame 2.6.1 (SDL 2.28.4, Python 3.13.7)
Hello from the pygame community.
 Found wake word model: .../Hey-Navi_en_mac_v3_0_0.ppn
 Wake word detection started successfully!
 Wake word detection active. Say 'Hey Navi' to activate...
```

---

##  Microphone Setup

### Windows
1. Right-click the speaker icon in system tray
2. Select "Sounds" → "Recording" tab
3. Ensure your microphone is set as default
4. Test by speaking and watching the level indicator

### macOS
1. Open System Preferences → Sound
2. Click "Input" tab
3. Select your microphone
4. Adjust input volume
5. Test by speaking and watching the level indicator

### Linux
```bash
# List audio devices
arecord -l

# Test microphone
arecord -d 5 test.wav
aplay test.wav
```

---

##  Audio Output Setup

### Test Audio Output
Navi will speak responses using ElevenLabs text-to-speech. Ensure:
- Speakers/headphones are connected
- Volume is at a comfortable level
- Audio output device is set correctly in system settings

---

##  Common Installation Issues

### Issue: `pip: command not found`
**Solution:**
```bash
# Windows
python -m pip install -r requirements.txt

# macOS/Linux
python3 -m pip install -r requirements.txt
```

### Issue: `ModuleNotFoundError: No module named 'customtkinter'`
**Solution:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Issue: `Permission denied` (macOS/Linux)
**Solution:**
```bash
sudo pip install -r requirements.txt
# OR use virtual environment (recommended)
```

### Issue: Wake word not detected
**Solution:**
1. Check microphone permissions in system settings
2. Verify microphone is working in other apps
3. Ensure `PICOVOICE_ACCESS_KEY` is correct in `.env`

### Issue: `API key invalid` errors
**Solution:**
1. Verify API keys are copied correctly (no extra spaces)
2. Check that keys have proper permissions
3. See [API Keys Setup Guide](API-Keys-Setup.md) for details

---

##  Updating Navi

### Using Git
```bash
cd Navi
git pull origin main
pip install -r requirements.txt --upgrade
```

### Manual Update
1. Download the latest release from GitHub
2. Extract and replace old files
3. Run `pip install -r requirements.txt --upgrade`

---

##  Post-Installation Checklist

- [ ] Python 3.13+ installed
- [ ] Repository cloned/downloaded
- [ ] Virtual environment created (optional but recommended)
- [ ] Dependencies installed
- [ ] `.env` file created with valid API keys
- [ ] Microphone working and set as default
- [ ] Audio output working
- [ ] Navi starts without errors
- [ ] Wake word detection active

---

##  Next Steps

1. **[Quick Start Guide](Quick-Start.md)** - Learn basic usage
2. **[Voice Commands](Voice-Commands.md)** - Explore what you can ask
3. **[How to Use Navi](How-to-Use-Navi.md)** - Complete user manual

---

##  Tips for Success

- **Use a quiet environment** for better voice recognition
- **Speak clearly** at a normal pace
- **Position microphone** 6-12 inches from your mouth
- **Update regularly** to get the latest features and fixes

---

**Need more help?** Check the [Troubleshooting Guide](Troubleshooting.md) or [open an issue](https://github.com/Vetri213/Navi/issues).
