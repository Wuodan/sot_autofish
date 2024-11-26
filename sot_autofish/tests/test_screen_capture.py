import mss
import time

def capture_screenshots(interval=1, output_folder="screenshots"):
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Capture primary monitor
        count = 0
        while True:
            filename = f"{output_folder}/screenshot_{count:04d}.png"
            sct.shot(mon=1, output=filename)
            print(f"Captured {filename}")
            count += 1
            time.sleep(interval)

capture_screenshots()
