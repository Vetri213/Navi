import sys
from PySide6.QtWidgets import QApplication
from core.gemini_handler import configure_gemini
from UI.navi_assistant import NaviAssistant
from core.voice_handler import speak_with_eleven

if __name__ == "__main__":
    configure_gemini()
    app = QApplication(sys.argv)
    window = NaviAssistant()
    window.show()
    sys.exit(app.exec())
