import win32gui
import win32api
import win32con
import time


def send_key(hwnd, key):
    """Send a key press to the target window."""
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, key, 0)
    time.sleep(0.05)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, key, 0)


def send_mouse_click(hwnd, x, y, button="left"):
    """Send a mouse click to the target window at (x, y)."""
    lParam = win32api.MAKELONG(x, y)
    if button == "left":
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
    elif button == "right":
        win32api.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
        win32api.PostMessage(hwnd, win32con.WM_RBUTTONUP, 0, lParam)


if __name__ == "__main__":
    # Replace with the window title of your game
    hwnd = win32gui.FindWindow(None, "Sea of Thieves")
    if hwnd:
        print("Sending input to 'Sea of Thieves'")

        # Example: Send 'F' key
        send_key(hwnd, ord('f'))
        time.sleep(1)

        # Example: Send a left mouse click at coordinates (200, 300)
        send_mouse_click(hwnd, x=200, y=300, button="left")
        time.sleep(1)

        # Example: Send a right mouse click at coordinates (400, 500)
        send_mouse_click(hwnd, x=400, y=500, button="right")
    else:
        print("Window not found.")
