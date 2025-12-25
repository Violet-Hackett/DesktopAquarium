import pygame
import win32gui
import win32ui
import win32con
from runtime_resources import *
import ctypes
import state

screen_capture_buffer: pygame.Surface | None = None
window_position_buffer: tuple[float, float, float, float] | None = None

def check_window_movement() -> bool:
    global window_position_buffer

    # Capture window position
    hwnd = pygame.display.get_wm_info()["window"]
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    x, y = win32gui.ClientToScreen(hwnd, (left, top))
    w, h = right - left, bottom - top

    if (x, y, w, h) != window_position_buffer or not window_position_buffer:
        window_position_buffer = (x, y, w, h)
        return True
    return False

user32 = ctypes.windll.user32
ctypes.windll.shcore.SetProcessDpiAwareness(2)
def pull_screen_capture() -> pygame.Surface:
    global screen_capture_buffer

    if check_window_movement() or not screen_capture_buffer or state.frame_count == 2:
        hwnd = pygame.display.get_wm_info()["window"]

        # Store original full-window position
        orig_rect = win32gui.GetWindowRect(hwnd)
        orig_x, orig_y, orig_right, orig_bottom = orig_rect
        w, h = orig_right - orig_x, orig_bottom - orig_y

        # Store original client position
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        x, y = win32gui.ClientToScreen(hwnd, (left, top))
        cw, ch = right - left, bottom - top

        # Move window offscreen
        win32gui.SetWindowPos(hwnd, None, -10000, -10000, w, h,
                            win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW)

        # Capture the client area
        screen_capture_buffer = capture_to_surface(x, y, cw, ch)

        # Restore window to original position
        win32gui.SetWindowPos(hwnd, None, orig_x, orig_y, w, h,
                            win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW)

    return screen_capture_buffer

def capture_to_surface(x, y, w, h):
    hwnd = 0  # desktop
    hdc = win32gui.GetDC(hwnd)
    srcdc = win32ui.CreateDCFromHandle(hdc)
    memdc = srcdc.CreateCompatibleDC()

    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, w, h)
    memdc.SelectObject(bmp)

    memdc.BitBlt((0, 0), (w, h), srcdc, (x, y), win32con.SRCCOPY)

    # Prepare bitmap info
    bmpinfo = bmp.GetInfo()
    bmpstr = bmp.GetBitmapBits(True)

    # Create pygame surface (BGRA → RGBA)
    surface = pygame.image.frombuffer(
        bmpstr,
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        'BGRA'
    )

    surface = surface.convert_alpha()

    # Cleanup
    memdc.DeleteDC()
    srcdc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hdc)
    win32gui.DeleteObject(bmp.GetHandle())

    return surface