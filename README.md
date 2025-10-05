# 🧭 Navi - Your Personal Computer Navigation Assistant

<div align="center">

![Navi Logo](https://img.shields.io/badge/Navi-AI%20Assistant-7C3AED?style=for-the-badge&logo=robot&logoColor=white)
[![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Empowering the elderly and non-technical users to navigate their computers with confidence**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Technology](#-technology-stack)

</div>

---

## 🌟 Overview

**Navi** is an intelligent, voice-activated computer navigation assistant designed specifically to help elderly users and those less familiar with technology navigate their computers effortlessly. Named after the helpful companion from *The Legend of Zelda*, Navi guides users through complex computer tasks with simple, step-by-step voice instructions.

### The Problem We Solve

Many elderly individuals struggle with basic computer tasks that younger generations take for granted:
- Finding and opening applications
- Navigating system settings
- Searching for files and folders
- Using web browsers effectively
- Understanding error messages

**Navi bridges this digital divide** by providing real-time, context-aware assistance through natural voice interaction.

---

##  Features

###  **Wake Word Detection**
- Simply say **"Hey Navi"** to activate the assistant
- No need to click buttons or navigate menus
- Always listening, always ready to help

###  **Natural Voice Interaction**
- Speak naturally - no need to memorize commands
- Ask questions like: *"Help me find my photos"* or *"How do I print this document?"*
- Powered by ElevenLabs speech recognition for accurate transcription

###  **Context-Aware Screenshot Analysis**
- Navi automatically captures your screen to understand what you're looking at
- Uses Google Gemini AI to analyze the visual context
- Provides specific, actionable guidance based on your current screen

###  **Step-by-Step Guidance**
- Clear, numbered instructions that are easy to follow
- Context-aware follow-up questions: *"Do you see it?"* or *"Did that work?"*
- Adaptive clarification when you need more help

###  **Beautiful, Accessible UI**
- Clean, modern interface with large, readable text
- High-contrast colors for better visibility
- Floating assistant that stays on top of other windows
- Minimal design to avoid overwhelming users

###  **Natural Voice Responses**
- Navi speaks back to you with natural, human-like voice
- Hands-free operation - perfect for users with limited mobility
- Automatic yes/no detection for seamless conversation flow

---

## Demo

### Typical User Journey

1. **User says:** *"Hey Navi"*
   - Navi activates and starts listening

2. **User asks:** *"Help me find a pizzeria near me"*
   - Navi takes a screenshot of the current screen
   - Analyzes what's visible
   - Provides step-by-step instructions

3. **Navi responds:**
   ```
   Step 1 of 3
   
   Open your web browser by clicking the Chrome icon on your desktop.
   
   Do you see it?
   ```

4. **User responds:** *"Yes"*
   - Navi moves to the next step automatically

5. **Navi continues:**
   ```
   Step 2 of 3
   
   Type "pizzeria near me" in the search bar at the top of the screen.
   
   Did you finish typing that?
   ```

---

## Installation

### Prerequisites

- **Python 3.13+**
- **Microphone** for voice input
- **Internet connection** for AI services

### Step 1: Clone the Repository

```bash
git clone https://github.com/Vetri213/Navi.git
cd Navi
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up API Keys

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
ELEVEN_API_KEY=your_elevenlabs_api_key_here
PICOVOICE_ACCESS_KEY=your_picovoice_access_key_here
```

#### Getting API Keys:

1. **Google Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy and paste into `.env`

2. **ElevenLabs API Key**
   - Sign up at [ElevenLabs](https://elevenlabs.io/)
   - Navigate to your profile settings
   - Generate an API key with `speech_to_text` permission
   - Copy and paste into `.env`

3. **Picovoice Access Key**
   - Create an account at [Picovoice Console](https://console.picovoice.ai/)
   - Generate an access key for Porcupine (wake word detection)
   - Copy and paste into `.env`

### Step 4: Download Wake Word Model

The custom "Hey Navi" wake word model is included in the repository at:
```
Hey-Navi_en_mac_v3_0_0/Hey-Navi_en_mac_v3_0_0.ppn
```

---

##  Usage

### Starting Navi

```bash
python main.py
```

### Basic Commands

Once Navi is running:

1. **Activate:** Say *"Hey Navi"*
2. **Ask for help:** Speak your request naturally
3. **Respond:** Say *"Yes"* to continue or *"No"* for clarification
4. **Close:** Click the × button in the top-right corner

### Example Use Cases

#### Finding Applications
- *"Hey Navi, help me open Microsoft Word"*
- *"How do I find my email?"*
- *"Where is the calculator app?"*

#### System Settings
- *"Help me change my wallpaper"*
- *"How do I make the text bigger?"*
- *"Show me how to connect to WiFi"*

#### File Management
- *"Help me find my photos from last year"*
- *"How do I save this document?"*
- *"Where are my downloads?"*

#### Web Browsing
- *"Help me search for a recipe"*
- *"How do I book a doctor's appointment online?"*
- *"Find a dentist near me"*

---

## 🛠️ Technology Stack

### Core Technologies

| Technology | Purpose |
|------------|---------|
| **Python 3.13** | Core programming language |
| **CustomTkinter** | Modern, beautiful UI framework |
| **Google Gemini 2.0 Flash** | Advanced vision and language AI for context understanding |
| **ElevenLabs** | High-quality speech-to-text and text-to-speech |
| **Picovoice Porcupine** | Wake word detection ("Hey Navi") |
| **PyAutoGUI** | Screen capture functionality |
| **Pygame** | Audio playback for voice responses |

### AI Capabilities

- **Vision AI:** Analyzes screenshots to understand user context
- **Natural Language Processing:** Interprets user requests in plain English
- **Conversational AI:** Maintains context across multi-turn conversations
- **Voice Recognition:** Accurate transcription even with accents or background noise

---

## 🏗️ Project Structure

```
Navi/
├── main.py                          # Application entry point
├── core/
│   ├── gemini_handler.py           # Google Gemini AI integration
│   ├── voice_handler.py            # Speech recognition & synthesis
│   ├── screenshot_handler.py       # Screen capture functionality
│   └── wake_word_handler.py        # "Hey Navi" detection
├── UI/
│   └── navi_assistant.py           # User interface components
├── Hey-Navi_en_mac_v3_0_0/         # Wake word model
│   └── Hey-Navi_en_mac_v3_0_0.ppn
├── requirements.txt                 # Python dependencies
├── .env                            # API keys (not in repo)
└── README.md                       # This file
```

---

##  Design Philosophy

### 1. **Simplicity First**
Every feature is designed to be intuitive. No technical jargon, no complex menus.

### 2. **Voice-First Interaction**
Hands-free operation reduces barriers for users with limited dexterity or vision.

### 3. **Context Awareness**
Navi sees what you see and provides relevant, specific guidance.

### 4. **Patient & Adaptive**
If you don't understand, Navi will explain differently. No judgment, no frustration.

### 5. **Always Available**
Wake word detection means help is always just a phrase away.

---

##  Impact & Vision

### Who Benefits?

- **Elderly Users:** Navigate technology with confidence and independence
- **Caregivers:** Reduce time spent providing tech support
- **Non-Technical Users:** Learn computer skills through guided practice
- **Accessibility Needs:** Voice-first design helps users with visual or motor impairments

### Future Roadmap

- [ ] **Multi-language support** for non-English speakers
- [ ] **Windows & Linux compatibility**
- [ ] **Mobile app** for smartphone assistance
- [ ] **Customizable voice personas**
- [ ] **Offline mode** for basic functionality
- [ ] **Learning mode** that adapts to user skill level
- [ ] **Family dashboard** for remote assistance
- [ ] **Integration with smart home devices**

---

##  Contributing

We welcome contributions! Whether you're fixing bugs, adding features, or improving documentation, your help makes Navi better for everyone.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---



## 🙏 Acknowledgments

- **Picovoice** for wake word detection technology
- **ElevenLabs** for natural voice synthesis
- **Google** for Gemini AI capabilities
- **The elderly community** for inspiring this project

---

<div align="center">

**Made with ❤️ for everyone who deserves technology that works for them**



</div>
