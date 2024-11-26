import pyautogui
import time

# Step 1: Cast the fishing rod
time.sleep(2)  # Wait for the game window
pyautogui.press('f')  # Simulate 'F' key to cast the line

# Step 2: Wait for visual/audio cue (manual observation or later automation)
time.sleep(10)  # Placeholder for fish bite

# Step 3: Simulate reeling in
for _ in range(20):
    pyautogui.keyDown('left')  # Simulate holding left key
    time.sleep(0.1)
    pyautogui.keyUp('left')
