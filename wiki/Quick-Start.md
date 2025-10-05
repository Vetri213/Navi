# Quick Start Guide

Get up and running with Navi in just 5 minutes! 

---

##  Prerequisites

Before starting, ensure you have:
-  Completed the [Installation Guide](Installation-Guide.md)
-  Set up your [API Keys](API-Keys-Setup.md)
-  A working microphone
-  Speakers or headphones

---

##  First Time Setup

### Step 1: Start Navi

Open your terminal and navigate to the Navi directory:

```bash
cd /path/to/Navi
python main.py
```

You should see:
```
 Loading .env from: /path/to/.env
 ELEVEN_API_KEY loaded: Yes
pygame 2.6.1 (SDL 2.28.4, Python 3.13.7)
Hello from the pygame community.
 Found wake word model
 Wake word detection started successfully!
 Wake word detection active. Say 'Hey Navi' to activate...
```

### Step 2: The Navi Interface

A small purple button labeled **"ASK NAVI"** will appear in the bottom-right corner of your screen.

![Navi Button](https://via.placeholder.com/180x56/7C3AED/FFFFFF?text=ASK+NAVI)

This button:
- 🟣 **Stays on top** of all windows
-  **Can be dragged** anywhere on screen
-  **Activates** when you say "Hey Navi"
-  **Can be clicked** to open manually

---

##  Your First Interaction

### Method 1: Using Wake Word (Recommended)

1. **Say:** *"Hey Navi"*
   - The button will bounce
   - The panel will expand
   - Navi will start listening

2. **Ask your question:**
   - *"Help me find a pizzeria near me"*
   - Speak naturally and clearly
   - Wait for Navi to process

3. **Follow the steps:**
   - Navi will provide step-by-step instructions
   - Listen to the voice guidance
   - Respond with "Yes" or "No"

### Method 2: Manual Activation

1. **Click** the purple "ASK NAVI" button
2. **Click** the microphone icon 
3. **Speak** your request
4. **Follow** the instructions

---

##  Example Conversation

Here's what a typical interaction looks like:

**You:** *"Hey Navi"*

**Navi:**  *Listening...*

**You:** *"Help me find a pizzeria near me"*

**Navi:**  *Taking screenshot and analyzing...*

**Navi:**  *"Step 1 of 3: Open your web browser by clicking the Chrome icon on your desktop. Do you see it?"*

**You:** *"Yes"*

**Navi:**  *"Step 2 of 3: Type 'pizzeria near me' in the search bar at the top. Did you finish typing that?"*

**You:** *"Yes"*

**Navi:**  *"Step 3 of 3: Click on the first result to see details about the pizzeria. Did that work?"*

**You:** *"Yes"*

**Navi:**  *"All steps completed! Great job!"*

---

##  What Can You Ask?

### Common Requests

#### Finding Things
- *"Help me find my photos"*
- *"Where is Microsoft Word?"*
- *"How do I find my downloads?"*

#### Opening Applications
- *"Help me open my email"*
- *"How do I start a video call?"*
- *"Open the calculator"*

#### System Settings
- *"Help me change my wallpaper"*
- *"How do I make the text bigger?"*
- *"Connect to WiFi"*

#### Web Browsing
- *"Help me search for a recipe"*
- *"Find a dentist near me"*
- *"How do I book a doctor's appointment?"*

#### File Management
- *"Help me save this document"*
- *"How do I print this?"*
- *"Where did I save that file?"*

---

##  Voice Interaction Tips

### For Best Results

 **DO:**
- Speak clearly at a normal pace
- Use natural language
- Wait for Navi to finish speaking
- Respond with "Yes" or "No" when asked
- Ask for clarification if confused

 **DON'T:**
- Shout or whisper
- Speak too fast
- Interrupt while Navi is speaking
- Use technical jargon
- Give up after one try!

### If Navi Doesn't Understand

1. **Try rephrasing:** *"Help me find a restaurant"* instead of *"Locate dining establishment"*
2. **Be more specific:** *"Open Google Chrome"* instead of *"Open browser"*
3. **Click "No, Clarify"** to get more detailed instructions

---

##  Using the Interface

### Expanded Panel

When Navi activates, you'll see:

```

  Navi Assistant               ×     

  [Animation Wave]                   

  What do you need help with?      
  [Input Box]                        

  [Get Help Button]                  

  Step 1 of 3                        
                                     
  Instructions appear here...        
                                     
  Did that work?                     

  [Yes, Next Step] [No, Clarify]     

```

### Button Functions

- ** Microphone:** Click to use voice input
- **Get Help:** Process your typed request
- **Yes, Next Step:** Move to next instruction
- **No, Clarify:** Get more detailed explanation
- **× Close:** Minimize back to button

---

##  Typical Workflow

```
1. Say "Hey Navi" or click button
         ↓
2. Panel expands & starts listening
         ↓
3. Speak your request
         ↓
4. Navi takes screenshot
         ↓
5. AI analyzes your screen
         ↓
6. Navi provides step-by-step guidance
         ↓
7. Follow instructions
         ↓
8. Respond "Yes" or "No"
         ↓
9. Repeat until task complete
         ↓
10. Click × to close
```

---

##  Learning by Example

### Example 1: Finding an Application

**Scenario:** You want to open Microsoft Word but can't find it.

1. Say: *"Hey Navi"*
2. Say: *"Help me open Microsoft Word"*
3. Navi analyzes your desktop
4. Navi: *"Click the Windows Start button in the bottom-left corner"*
5. You click it
6. Say: *"Yes"*
7. Navi: *"Type 'Word' in the search box"*
8. You type it
9. Say: *"Yes"*
10. Navi: *"Click on Microsoft Word in the results"*
11. Done! 

### Example 2: Changing Settings

**Scenario:** You want to make text bigger on your screen.

1. Say: *"Hey Navi"*
2. Say: *"Help me make the text bigger"*
3. Navi: *"Open Settings by clicking the gear icon"*
4. You: *"I don't see it"*
5. Navi: *"Let me explain better... Look in the Start menu..."*
6. Continue following steps
7. Complete! 

---

##  Basic Settings

### Adjusting Microphone

If Navi has trouble hearing you:

**Windows:**
1. Right-click speaker icon → Sounds
2. Recording tab → Select microphone
3. Properties → Levels → Increase volume

**macOS:**
1. System Preferences → Sound
2. Input tab → Select microphone
3. Adjust input volume slider

### Adjusting Volume

If Navi is too loud or quiet:
- Use your system volume controls
- Adjust speaker/headphone volume
- Check Navi doesn't have separate volume control

---

##  Quick Troubleshooting

### Navi doesn't respond to "Hey Navi"
- Check microphone is working
- Verify `PICOVOICE_ACCESS_KEY` in `.env`
- Try clicking the button manually

### Voice recognition doesn't work
- Check `ELEVEN_API_KEY` in `.env`
- Ensure internet connection is stable
- Try speaking more clearly

### No voice responses
- Check speakers/headphones are connected
- Verify system volume is up
- Check `ELEVEN_API_KEY` has proper permissions

### Panel disappears
- This is normal when taking screenshots
- It should reappear after processing
- If stuck, restart Navi

---

##  Quick Start Checklist

- [ ] Navi starts without errors
- [ ] "Hey Navi" activates the assistant
- [ ] Voice recognition works
- [ ] Navi speaks responses
- [ ] Can follow step-by-step instructions
- [ ] "Yes" and "No" responses work
- [ ] Can close and reopen panel

---

##  You're Ready!

Congratulations! You're now ready to use Navi. 

### Next Steps

1. **[Explore Voice Commands](Voice-Commands.md)** - Learn all available commands
2. **[Read Common Use Cases](Common-Use-Cases.md)** - See real-world examples
3. **[Full User Manual](How-to-Use-Navi.md)** - Deep dive into all features

---

##  Pro Tips

- **Practice makes perfect:** The more you use Navi, the better you'll get
- **Be patient:** AI processing takes a few seconds
- **Ask for help:** Use "No, Clarify" whenever you're confused
- **Experiment:** Try different ways of asking the same question
- **Stay calm:** Navi is here to help, not judge!

---

**Need more help?** Check the [FAQ](FAQ.md) or [Troubleshooting Guide](Troubleshooting.md)!
