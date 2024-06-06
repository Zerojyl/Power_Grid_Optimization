from stable_baselines3 import PPO


class PPOAgent:
    def __init__(self, model_path):
        self.agent = PPO.load(model_path)

    def act(self, obs):
        action, _ = self.agent.predict(obs, deterministic=True)
        return action