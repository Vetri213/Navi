import pyautogui

def take_screenshot():
    """
    Takes a screenshot of the entire screen.
    This function no longer handles hiding/showing windows.
    """
    try:
        screenshot = pyautogui.screenshot()
        return screenshot
    except Exception as e:
        print(f"Screenshot error: {e}")
        return None
