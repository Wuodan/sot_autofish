from stable_baselines3 import DQN
from game_fishing_env import GameFishingEnv

# Load the trained model
model = DQN.load("fishing_ai")

# Initialize the environment
env = GameFishingEnv()

# Use the model to predict actions
obs = env.reset()
while True:
    action, _ = model.predict(obs)
    obs, reward, done, _ = env.step(action)
    if done:
        obs = env.reset()
