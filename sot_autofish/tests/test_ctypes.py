import ctypes
import time

USER32 = ctypes.windll.user32

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class InputI(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", InputI)]


# Constants for key events
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002

# Virtual-Key Codes for A, S, D, F
KEY_MAP = {
    'a': 0x1E,
    's': 0x1F,
    'd': 0x20,
    'f': 0x21,
}

# Constants for mouse events
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010


def press_key(scancode):
    """Press a key using its scancode."""
    extra = ctypes.c_ulong(0)
    ii_ = InputI()
    ii_.ki = KeyBdInput(0, scancode, KEYEVENTF_SCANCODE, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    USER32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def release_key(scancode):
    """Release a key using its scancode."""
    extra = ctypes.c_ulong(0)
    ii_ = InputI()
    ii_.ki = KeyBdInput(0, scancode, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    USER32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def left_click():
    """Perform a left mouse click."""
    extra = ctypes.c_ulong(0)
    ii_ = InputI()
    ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_)
    USER32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_)
    USER32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def right_click():
    """Perform a right mouse click."""
    extra = ctypes.c_ulong(0)
    ii_ = InputI()

    # Right button down
    ii_.mi = MouseInput(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_RIGHTDOWN, time=0,
                        dwExtraInfo=ctypes.pointer(extra))
    x = Input(type=ctypes.c_ulong(0), ii=ii_)
    USER32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    # Right button up
    ii_.mi = MouseInput(dx=0, dy=0, mouseData=0, dwFlags=MOUSEEVENTF_RIGHTUP, time=0,
                        dwExtraInfo=ctypes.pointer(extra))
    x = Input(type=ctypes.c_ulong(0), ii=ii_)
    USER32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def find_window(title):
    hwnd = USER32.FindWindowW(None, title)
    return hwnd


if __name__ == "__main__":
    hwnd = find_window("Sea of Thieves")
    USER32.SetForegroundWindow(hwnd)
    time.sleep(2)  # Give time to switch to the game window
    # Example: Send 'F' key
    press_key(KEY_MAP['f'])
    time.sleep(0.1)
    release_key(KEY_MAP['f'])
    time.sleep(2)

    # Example: Send left click
    left_click()
    print("sent left click")
    time.sleep(2)

    # Example: Send right click
    right_click()
    print("sent right click")
