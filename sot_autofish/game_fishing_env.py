"""Custom Gymnasium environment for Sea of Thieves fishing."""
import gymnasium as gym
import numpy as np
import cv2
import mss
import pyautogui
from gymnasium import spaces


class GameFishingEnv(gym.Env):
    """Custom environment for automating fishing in Sea of Thieves."""
    def __init__(self):
        super().__init__()
        # Define the action space: 0=F, 1=D, 2=A, 3=S
        self.action_space = spaces.Discrete(4)

        # Observation space: Grayscale game screen (84x84)
        self.observation_space = spaces.Box(low=0, high=255, shape=(84, 84, 1), dtype=np.uint8)

        # Screen capture region (adjust for your monitor/game resolution)
        self.monitor = {"top": 100, "left": 100, "width": 800, "height": 600}
        self.previous_frame = None  # To detect changes for rewards

    def reset(self, seed=None, options=None):
        """Reset the environment and return the initial observation."""
        super().reset(seed=seed)
        self.previous_frame = self._get_screen_frame()
        initial_state = self._process_frame(self.previous_frame)
        return initial_state, {}

    def step(self, action):
        """Take an action in the environment and return the result."""
        self._perform_action(action)

        # Wait for a short time to let the game respond
        pyautogui.sleep(0.5)

        # Get the new game state
        current_frame = self._get_screen_frame()
        processed_frame = self._process_frame(current_frame)

        # Calculate reward based on game state changes
        reward = self._calculate_reward(self.previous_frame, current_frame, action)
        self.previous_frame = current_frame

        # Determine if the episode is done (e.g., fish caught)
        done = self._check_if_done(current_frame)

        return processed_frame, reward, done, False, {}

    def _get_screen_frame(self):
        """Capture the current screen and return it as a NumPy array."""
        with mss.mss() as sct:
            frame = np.array(sct.grab(self.monitor))
        return frame

    def _process_frame(self, frame):
        """Convert a screen frame to grayscale and resize it."""
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized_frame = cv2.resize(gray_frame, (84, 84))
        return np.expand_dims(resized_frame, axis=-1)  # Add channel dimension

    def _perform_action(self, action):
        """Simulate a keypress for the given action."""
        keys = ['f', 'd', 'a', 's']
        pyautogui.press(keys[action])

    def _calculate_reward(self, previous_frame, current_frame, action):
        """Calculate the reward based on the change in screen state."""
        diff = cv2.absdiff(previous_frame, current_frame)
        movement_change = np.sum(diff)

        # Define rewards/punishments based on game state changes
        if action == 0:  # F (cast rod or reel in fish)
            if movement_change < 500:  # Rod casting or reeling in is successful
                return 10
            return -5  # Nothing happened
        if action in [1, 2, 3]:  # D, A, S (reeling directions)
            if movement_change > 1000:  # Fish pulling in the expected direction
                return 5
            return -5  # Wrong action or no movement
        return 0  # Neutral reward

    def _check_if_done(self, frame):
        """Check if the fish has been successfully reeled in."""
        # Placeholder: Implement visual cue detection logic here
        return False
