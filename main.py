from core.gemini_handler import configure_gemini
from UI.navi_assistant import NaviAssistant

if __name__ == "__main__":
    configure_gemini()
    app = NaviAssistant()
    app.mainloop()