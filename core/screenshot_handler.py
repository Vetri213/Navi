import pyautogui, time

def take_screenshot(window):
    try:
        window.withdraw()
        time.sleep(0.3)
        screenshot = pyautogui.screenshot()
        window.deiconify()
        return screenshot
    except Exception as e:
        window.deiconify()
        print(f"Screenshot error: {e}")
        return None
