import win32gui
import win32con
import win32api
import time
from threading import Thread

class ScreenAnnotator:
    def __init__(self):
        self.hwnd = None
        self.class_atom = None
        self.region_rect = None

    # --- window creation ---------------------------------------------------
    def _create_overlay(self):
        hInstance = win32api.GetModuleHandle()
        className = "NaviOverlay"

        if not self.class_atom:
            wndClass = win32gui.WNDCLASS()
            wndClass.hInstance = hInstance
            wndClass.lpszClassName = className
            wndClass.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
            wndClass.hbrBackground = 0
            wndClass.lpfnWndProc = self._wnd_proc
            self.class_atom = win32gui.RegisterClass(wndClass)

        exStyle = (
            win32con.WS_EX_LAYERED
            | win32con.WS_EX_TRANSPARENT
            | win32con.WS_EX_TOPMOST
            | win32con.WS_EX_NOACTIVATE
        )

        width = win32api.GetSystemMetrics(0)
        height = win32api.GetSystemMetrics(1)
        style = win32con.WS_POPUP

        hwnd = win32gui.CreateWindowEx(
            exStyle,
            className,
            None,
            style,
            0, 0,
            width, height,
            0, 0, hInstance, None,
        )
        # make black fully transparent
        win32gui.SetLayeredWindowAttributes(hwnd, 0, 0, win32con.LWA_COLORKEY)
        self.hwnd = hwnd
        return hwnd

    # --- window procedure --------------------------------------------------
    def _wnd_proc(self, hwnd, msg, wparam, lparam):

        if msg == win32con.WM_PAINT:
            hdc, paintStruct = win32gui.BeginPaint(hwnd)
            win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
            if self.region_rect:
                pen = win32gui.CreatePen(win32con.PS_SOLID, 5, win32api.RGB(255, 0, 0))
                win32gui.SelectObject(hdc, pen)
                win32gui.SelectObject(hdc, win32con.NULL_BRUSH)
                win32gui.Rectangle(hdc, *self.region_rect)
                win32gui.DeleteObject(pen)
            win32gui.EndPaint(hwnd, paintStruct)
            return 0
        elif msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    # --- runtime loop ------------------------------------------------------
    def _run_overlay(self, duration):
        hwnd = self._create_overlay()
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        start = time.time()
        while time.time() - start < duration:
            win32gui.RedrawWindow(hwnd, None, None,
                                  win32con.RDW_INVALIDATE | win32con.RDW_UPDATENOW)
            time.sleep(0.05)
        win32gui.DestroyWindow(hwnd)

    # --- public API --------------------------------------------------------
    def highlight_region(self, area_hint, duration=2.0):
        width = win32api.GetSystemMetrics(0)
        height = win32api.GetSystemMetrics(1)
        regions = {
            "top": (0, 0, width, int(height * 0.2)),
            "bottom": (0, int(height * 0.8), width, height),
            "left": (0, 0, int(width * 0.2), height),
            "right": (int(width * 0.8), 0, width, height),
            "center": (int(width * 0.3), int(height * 0.3),
                       int(width * 0.7), int(height * 0.7)),
            "taskbar": (0, int(height * 0.9), width, height),
        }
        if area_hint not in regions:
            area_hint = "center"
        self.region_rect = regions[area_hint]
        Thread(target=self._run_overlay, args=(duration,), daemon=True).start()
