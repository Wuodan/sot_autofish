"""
Game Interaction Module

This module provides a utility class for interacting with a game window
via Windows system calls. It includes methods for sending keyboard and mouse
inputs, ensuring that the game window is active before any interaction.

Classes:
    GameWindowError: Custom exception raised for game window errors.
    GameInteraction: Utility class for managing and interacting with a game window.
"""

import ctypes
import random
import time
from enum import Enum
from typing import Optional

from sot_autofish.logger_setup.logger_setup import LoggerSetup

logger = LoggerSetup()

US_QWERTY_SCANCODES = {
    'a': 0x1E, 'b': 0x30, 'c': 0x2E, 'd': 0x20, 'e': 0x12, 'f': 0x21,
    'g': 0x22, 'h': 0x23, 'i': 0x17, 'j': 0x24, 'k': 0x25, 'l': 0x26,
    'm': 0x32, 'n': 0x31, 'o': 0x18, 'p': 0x19, 'q': 0x10, 'r': 0x13,
    's': 0x1F, 't': 0x14, 'u': 0x16, 'v': 0x2F, 'w': 0x11, 'x': 0x2D,
    'y': 0x15, 'z': 0x2C,
    '0': 0x0B, '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06,
    '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A,
    ' ': 0x39,  # Spacebar
    '\n': 0x1C,  # Enter
    '\b': 0x0E,  # Backspace
    '\t': 0x0F,  # Tab
}


class KeyScancode(Enum):
    """Enum for special keys and their scancodes."""
    CTRL = 0x1D  # Left Control
    LCTRL = 0x1D  # Left Control
    RCTRL = 0xE01D  # Right Control (extended scancode)
    SHIFT = 0x2A  # Left Shift
    LSHIFT = 0x2A  # Left Shift
    RSHIFT = 0x36  # Right Shift
    ALT = 0x38  # Left Alt
    LALT = 0x38  # Left Alt
    RALT = 0xE038  # Right Alt (extended scancode)
    TAB = 0x0F  # Tab key
    ENTER = 0x1C  # Enter key
    ESC = 0x01  # Escape key
    SPACE = 0x39  # Spacebar
    BACKSPACE = 0x0E  # Backspace key


class GameWindowError(Exception):
    """Custom exception raised when the game window is not in the foreground."""


class _KeyBdInput(ctypes.Structure):  # pylint: disable=too-few-public-methods
    """Data structure for keyboard input."""
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class _MouseInput(ctypes.Structure):  # pylint: disable=too-few-public-methods
    """Data structure for mouse input."""
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class _InputI(ctypes.Union):  # pylint: disable=too-few-public-methods
    """Union structure for input events."""
    _fields_ = [("ki", _KeyBdInput), ("mi", _MouseInput)]


class _Input(ctypes.Structure):  # pylint: disable=too-few-public-methods
    """Input structure for Windows API interactions."""
    _fields_ = [("type", ctypes.c_ulong), ("ii", _InputI)]


class GameInteraction:
    """Utility class for interacting with the game window."""
    _MOUSEEVENTF_LEFTDOWN = 0x0002
    _MOUSEEVENTF_LEFTUP = 0x0004
    _MOUSEEVENTF_RIGHTDOWN = 0x0008
    _MOUSEEVENTF_RIGHTUP = 0x0010
    _KEYEVENTF_SCANCODE = 0x0008
    _KEYEVENTF_KEYUP = 0x0002

    def __init__(self, game_title: str) -> None:
        """Initialize the GameInteraction utility."""
        self._user32 = ctypes.windll.user32
        self._set_to_foreground(game_title)
        self._keys_down = set()  # Track keys currently pressed down

    def _set_to_foreground(self, game_title: str) -> None:
        """Set the game window to the foreground."""
        hwnd: Optional[int] = self._user32.FindWindowW(None, game_title)
        if not hwnd:
            raise GameWindowError(f"Game window with title '{game_title}' not found.")
        result = self._user32.SetForegroundWindow(hwnd)
        if not result:
            raise GameWindowError("Failed to bring the game window to the foreground.")

    def _send_input(self, input_struct: _Input) -> None:
        """Send input to the game window."""
        result = self._user32.SendInput(1, ctypes.pointer(input_struct),
                                        ctypes.sizeof(input_struct))
        if not result:
            raise OSError("Failed to send input to the game window.")

    def _hold_key(self, key: str) -> None:
        """Press a key in the game if it's not already pressed."""
        if key in self._keys_down:
            logger.info("Key '%s' is already pressed. Ignoring press_key.", key)
            return  # Avoid sending a duplicate key-down event

        scancode = self._char_to_scancode(key)
        logger.info("Sending key-down for '%s' with scancode '%s'.", key, scancode)
        self._send_input(self._create_keyboard_input(scancode, self._KEYEVENTF_SCANCODE))
        self._keys_down.add(key)  # Mark the key as pressed

    def hold_key(self, key: str) -> None:
        """Hold a key in the game."""
        self._hold_key(key)
        self._random_sleep_after_key()

    def _release_key(self, key: str) -> None:
        """Release a key in the game."""
        if key not in self._keys_down:
            logger.info("Key '%s' is not pressed. Ignoring release_key.", key)
            return  # Avoid sending a release event for an unpressed key

        scancode = self._char_to_scancode(key)
        logger.info("Sending key-up for '%s' with scancode '%s'.", key, scancode)
        self._send_input(
            self._create_keyboard_input(scancode, self._KEYEVENTF_SCANCODE | self._KEYEVENTF_KEYUP)
        )
        self._keys_down.remove(key)  # Mark the key as released

    def release_key(self, key: str) -> None:
        """Release a key in the game."""
        self._release_key(key)
        self._random_sleep_after_key()

    def press_key(self, key: str) -> None:
        """Press and release a key in the game."""
        logger.info("Press and release '%s'.", key)
        self._hold_key(key)
        self._random_sleep_after_key(min_ms=50, max_ms=100)
        self._release_key(key)
        self._random_sleep_after_key()

    def reset_keys(self) -> None:
        """Release all keys that are currently pressed (for cleanup)."""
        for key in list(self._keys_down):  # Make a copy to avoid modification during iteration
            self._release_key(key)

    def left_click(self) -> None:
        """Perform a left mouse click."""
        self.left_click_down()
        self.left_click_up()

    def left_click_down(self) -> None:
        """Press the left mouse button down."""
        self._send_input(self._create_mouse_input(self._MOUSEEVENTF_LEFTDOWN))

    def left_click_up(self) -> None:
        """Release the left mouse button."""
        self._send_input(self._create_mouse_input(self._MOUSEEVENTF_LEFTUP))

    def right_click(self) -> None:
        """Perform a right mouse click."""
        self.right_click_down()
        self.right_click_up()

    def right_click_down(self) -> None:
        """Press the right mouse button down."""
        self._send_input(self._create_mouse_input(self._MOUSEEVENTF_RIGHTDOWN))

    def right_click_up(self) -> None:
        """Release the right mouse button."""
        self._send_input(self._create_mouse_input(self._MOUSEEVENTF_RIGHTUP))

    @staticmethod
    def _create_keyboard_input(scancode: int, flags: int) -> _Input:
        """Create a keyboard input structure."""
        return _Input(
            type=1,
            ii=_InputI(
                ki=_KeyBdInput(
                    wVk=0,
                    wScan=scancode,
                    dwFlags=flags,
                    time=0,
                    dwExtraInfo=ctypes.pointer(ctypes.c_ulong(0)),
                )
            ),
        )

    @staticmethod
    def _create_mouse_input(flags: int) -> _Input:
        """Create a mouse input structure."""
        return _Input(
            type=0,
            ii=_InputI(
                mi=_MouseInput(
                    dx=0,
                    dy=0,
                    mouseData=0,
                    dwFlags=flags,
                    time=0,
                    dwExtraInfo=ctypes.pointer(ctypes.c_ulong(0)),
                )
            ),
        )

    @staticmethod
    def _char_to_scancode(key: str) -> int:
        """
        Convert a key (character or special) to its scancode using the US QWERTY standard.

        Args:
            key (str): The key to convert. Can be a single character.

        Returns:
            int: The scancode for the given key.

        Raises:
            ValueError: If the key cannot be converted.
        """
        # Convert key to lowercase for consistent matching
        key = key.lower()

        # Check predefined US-QWERTY scancode map
        if key in US_QWERTY_SCANCODES:
            scancode = US_QWERTY_SCANCODES[key]
            logger.info( "Key '%s' -> scancode `%s', `%#04x'.", key, scancode, scancode)
            return scancode

        raise ValueError(f"Key '{key}' is not supported in the US-QWERTY scancode map.")

    @staticmethod
    def _random_sleep(min_ms: int, max_ms: int) -> None:
        """Sleep for a random duration between min_ms and max_ms milliseconds."""
        duration = random.uniform(min_ms / 1000, max_ms / 1000)  # Convert ms to seconds
        logger.debug("Sleeping for %.3f.", duration)
        time.sleep(duration)

    @staticmethod
    def _random_sleep_after_key(min_ms: int = 200, max_ms: int = 300) -> None:
        """Sleep for a random duration between min_ms and max_ms milliseconds."""
        GameInteraction._random_sleep(min_ms, max_ms)

    @staticmethod
    def _random_sleep_after_mouse(min_ms: int = 100, max_ms: int = 200) -> None:
        """Sleep for a random duration between min_ms and max_ms milliseconds."""
        GameInteraction._random_sleep(min_ms, max_ms)
