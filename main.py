from core.gemini_handler import configure_gemini
from UI.navi_assistant import NaviAssistant
from core.voice_handler import speak_with_eleven
#
# if __name__ == "__main__":
#     configure_gemini()
#     app = NaviAssistant()
#     app.mainloop()

from core.screen_annotator import ScreenAnnotator
import time

annotator = ScreenAnnotator()

annotator.highlight_region("taskbar", duration=2)
time.sleep(3)
annotator.highlight_region("top", duration=2)
time.sleep(3)
annotator.highlight_region("right", duration=2)
time.sleep(3)
