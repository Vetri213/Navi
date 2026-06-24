import time

from core.gemini_handler import configure_gemini
from UI.navi_assistant import NaviAssistant

if __name__ == "__main__":
    # speak_with_eleven("வணக்கம். இந்த திட்டத்தை உடனடியாக முடிக்க விரும்புகிறேன்.", voice_id="Z0ocGS7BSRxFSMhV00nB", on_finished=None)
    # time.sleep((15))
    configure_gemini()
    app = NaviAssistant()
    app.mainloop()