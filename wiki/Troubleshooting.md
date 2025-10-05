# Troubleshooting Guide

Solutions to common problems and issues with Navi.

---

##  Quick Diagnosis

### Is Navi Starting?

**Problem:** Navi won't start or crashes immediately

**Check:**
```bash
python main.py
```

Look for error messages in the output.

---

##  Wake Word Issues

### Problem: "Hey Navi" doesn't activate

#### Solution 1: Check Microphone Permissions

**macOS:**
1. System Preferences → Security & Privacy
2. Privacy tab → Microphone
3. Ensure Terminal/Python has microphone access

**Windows:**
1. Settings → Privacy → Microphone
2. Allow apps to access microphone
3. Ensure Python is allowed

**Linux:**
```bash
# Test microphone
arecord -d 3 test.wav
aplay test.wav
```

#### Solution 2: Verify Picovoice Key

```bash
# Check .env file
cat .env | grep PICOVOICE
```

Ensure:
- Key is present
- No extra spaces
- No quotes around the value

#### Solution 3: Check Wake Word Model

```bash
# Verify file exists
ls -la Hey-Navi_en_mac_v3_0_0/Hey-Navi_en_mac_v3_0_0.ppn
```

If missing, re-clone the repository.

#### Solution 4: Microphone Input Level

- Speak at normal volume
- Position microphone 6-12 inches away
- Reduce background noise
- Try saying "Hey Navi" more clearly

---

##  Voice Recognition Issues

### Problem: Navi doesn't understand what I'm saying

#### Solution 1: Check ElevenLabs API Key

```bash
# Verify key is loaded
python main.py
# Look for: " ELEVEN_API_KEY loaded: Yes"
```

If "No", check your `.env` file.

#### Solution 2: Check API Key Permissions

Error: `missing_permissions speech_to_text`

**Fix:**
1. Go to [ElevenLabs Dashboard](https://elevenlabs.io/)
2. Generate new API key with speech-to-text permission
3. Update `.env` file

#### Solution 3: Improve Voice Input

- **Speak clearly** at normal pace
- **Reduce background noise**
- **Use better microphone** if possible
- **Check microphone volume** in system settings

#### Solution 4: Network Issues

```bash
# Test internet connection
ping google.com
```

Voice recognition requires internet. Check:
- WiFi/Ethernet connection
- Firewall settings
- VPN interference

---

##  Audio Output Issues

### Problem: Can't hear Navi's voice responses

#### Solution 1: Check System Volume

- Ensure volume is not muted
- Check speaker/headphone connection
- Test with other audio (music, videos)

#### Solution 2: Check Audio Output Device

**macOS:**
1. System Preferences → Sound
2. Output tab
3. Select correct device

**Windows:**
1. Right-click speaker icon
2. Open Sound settings
3. Choose output device

#### Solution 3: Pygame Audio Issues

```bash
# Reinstall pygame
pip uninstall pygame
pip install pygame
```

#### Solution 4: ElevenLabs TTS Issues

Check terminal output for errors:
```
 ElevenLabs error: [error message]
```

Common fixes:
- Verify `ELEVEN_API_KEY` is correct
- Check internet connection
- Verify API quota not exceeded

---

##  Screenshot Issues

### Problem: Navi can't take screenshots

#### Solution 1: Check Permissions

**macOS:**
1. System Preferences → Security & Privacy
2. Privacy → Screen Recording
3. Enable for Terminal/Python

**Windows:**
- Usually no special permissions needed
- Check antivirus isn't blocking

#### Solution 2: PyAutoGUI Issues

```bash
# Reinstall pyautogui
pip uninstall pyautogui
pip install pyautogui
```

### Problem: Panel visible in screenshots

**Expected behavior:** Panel should hide before screenshot

If panel appears in screenshot:
1. Check `screenshot_handler.py` has proper delays
2. Increase `time.sleep()` value if needed
3. Report as bug on GitHub

---

##  AI/Gemini Issues

### Problem: Navi gives irrelevant or wrong guidance

#### Solution 1: Check Gemini API Key

```bash
# Check .env
cat .env | grep GEMINI
```

#### Solution 2: API Quota Exceeded

Error: `Quota exceeded` or `429 Too Many Requests`

**Fix:**
- Wait for quota to reset (daily/monthly)
- Check usage at [Google AI Studio](https://makersuite.google.com/)
- Consider upgrading if needed

#### Solution 3: Improve Screenshot Quality

- Ensure screen is visible (not covered)
- Close unnecessary windows
- Increase screen brightness
- Use higher resolution if possible

---

##  Installation Issues

### Problem: `ModuleNotFoundError`

```bash
ModuleNotFoundError: No module named 'customtkinter'
```

**Fix:**
```bash
pip install -r requirements.txt --force-reinstall
```

### Problem: `pip: command not found`

**Fix:**
```bash
# Windows
python -m pip install -r requirements.txt

# macOS/Linux
python3 -m pip install -r requirements.txt
```

### Problem: Permission denied (macOS/Linux)

```bash
# Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# OR use sudo (not recommended)
sudo pip install -r requirements.txt
```

### Problem: Python version too old

```bash
python --version
# Must be 3.13+
```

**Fix:**
- Install Python 3.13+ from [python.org](https://www.python.org/)
- Or use package manager (brew, apt, etc.)

---

##  API Key Issues

### Problem: "API key not valid"

#### Gemini
1. Verify key at [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Ensure key is enabled
3. Check for typos in `.env`

#### ElevenLabs
1. Verify key at [ElevenLabs Profile](https://elevenlabs.io/app/settings)
2. Regenerate if needed
3. Check permissions include speech-to-text

#### Picovoice
1. Verify key at [Picovoice Console](https://console.picovoice.ai/)
2. Ensure key is active
3. Check character encoding (no special characters)

### Problem: Keys not loading from .env

**Check:**
```bash
# File exists?
ls -la .env

# Correct format?
cat .env
```

**Correct format:**
```env
GEMINI_API_KEY=your_key_here
ELEVEN_API_KEY=your_key_here
PICOVOICE_ACCESS_KEY=your_key_here
```

**Common mistakes:**
-  Quotes around values: `GEMINI_API_KEY="key"`
-  Spaces: `GEMINI_API_KEY = key`
-  Wrong file location: `.env` must be in project root

---

##  UI Issues

### Problem: Panel doesn't appear

**Check:**
1. Is Navi running? Check terminal
2. Try clicking "ASK NAVI" button
3. Check if panel is off-screen (drag it back)

### Problem: Panel disappears and doesn't return

**This is a known issue.** Temporary fixes:

1. **Restart Navi:**
   ```bash
   # Press Ctrl+C in terminal
   python main.py
   ```

2. **Check terminal for errors:**
   - Look for Python exceptions
   - Report on GitHub if persistent

### Problem: Text too small/large

**Workaround:**
- Use system display scaling
- Request feature for adjustable UI size

---

##  Network Issues

### Problem: "Connection timeout" or "Network error"

**Check:**
1. Internet connection working?
2. Firewall blocking Python?
3. VPN causing issues?
4. Proxy settings?

**Test:**
```bash
# Test API connectivity
curl https://generativelanguage.googleapis.com/
curl https://api.elevenlabs.io/
```

---

##  Common Error Messages

### Error: `Picovoice Error (code 00000136)`

**Meaning:** Invalid Picovoice access key

**Fix:**
1. Check `PICOVOICE_ACCESS_KEY` in `.env`
2. Regenerate key at Picovoice Console
3. Ensure no extra spaces or characters

### Error: `missing_permissions speech_to_text`

**Meaning:** ElevenLabs key lacks speech-to-text permission

**Fix:**
1. Go to ElevenLabs dashboard
2. Generate new key with proper permissions
3. Update `.env` file

### Error: `ALTS creds ignored`

**Meaning:** Harmless warning from Google AI

**Fix:** Ignore this warning - it doesn't affect functionality

### Error: `ValueError: Missing GEMINI_API_KEY in .env`

**Meaning:** Gemini API key not found

**Fix:**
1. Check `.env` file exists
2. Verify `GEMINI_API_KEY=your_key` is present
3. No quotes around the key value

---

##  Reset & Reinstall

### Clean Reinstall

```bash
# 1. Backup your .env file
cp .env .env.backup

# 2. Remove virtual environment
rm -rf venv

# 3. Create new virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# 4. Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# 5. Restore .env
cp .env.backup .env

# 6. Test
python main.py
```

### Reset Configuration

```bash
# Remove cached files
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

---

##  Performance Issues

### Problem: Navi is slow to respond

**Causes:**
- Slow internet connection
- API rate limiting
- Low system resources

**Solutions:**
1. **Check internet speed:**
   ```bash
   # Run speed test
   curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python -
   ```

2. **Close other applications:**
   - Free up RAM
   - Reduce CPU usage

3. **Check API quotas:**
   - Gemini: [AI Studio](https://makersuite.google.com/)
   - ElevenLabs: [Dashboard](https://elevenlabs.io/)

### Problem: High CPU usage

**Normal:** Navi uses CPU for:
- Wake word detection (continuous)
- Voice processing
- AI inference

**If excessive:**
1. Close other applications
2. Check for runaway processes
3. Restart Navi

---

##  Still Need Help?

### Before Reporting an Issue

1. **Check this troubleshooting guide**
2. **Review [FAQ](FAQ.md)**
3. **Search [existing issues](https://github.com/Vetri213/Navi/issues)**
4. **Try clean reinstall**

### Reporting a Bug

Include:
- **Operating System:** (Windows/macOS/Linux version)
- **Python Version:** `python --version`
- **Error Message:** Full terminal output
- **Steps to Reproduce:** What you did before the error
- **Expected Behavior:** What should have happened
- **Actual Behavior:** What actually happened

**Open an issue:** [GitHub Issues](https://github.com/Vetri213/Navi/issues/new)

---

##  Related Resources

- **[Installation Guide](Installation-Guide.md)** - Proper setup instructions
- **[API Keys Setup](API-Keys-Setup.md)** - API key configuration
- **[Quick Start](Quick-Start.md)** - Basic usage guide
- **[FAQ](FAQ.md)** - Frequently asked questions

---

**Remember:** Most issues are related to API keys, microphone permissions, or internet connectivity. Check these first! 
