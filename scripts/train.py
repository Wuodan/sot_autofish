from pathlib import Path

from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env

from sot_autofish.game_fishing_env import GameFishingEnv

# Create and vectorize the environment
env = make_vec_env(GameFishingEnv, n_envs=1)

script_path = Path(__file__).resolve()
parent_folder = script_path.parent.parent
log_folder = parent_folder / 'logs'

# Initialize the DQN model
model = DQN("CnnPolicy", env, verbose=1, tensorboard_log=f"{log_folder}/fishing_tensorboard/")

# Train the agent
model.learn(total_timesteps=100000)

# Save the trained model
model.save("fishing_ai")
