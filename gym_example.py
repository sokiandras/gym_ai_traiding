import gym

include gym

class StockMarketEnv(gym.Env):
    def __init__(self, kezdő változók):
        alap változók
        adatlekérés

        observation space
        action space


    def get_observation(self):
        (adatok normálás)
        observation = adatok berendezése, amiket az adott számú lépésnél kap

        return observation


    def reset(self):
        kezdő értékek beállítása
        (lépésszám, balance, profit, vételek és eladások száma,... )


    def take_action(self, action):
        milyen action esetén mit csináljon

        return self.current_info


    def step(self, action):
        current_info = self.take_action(action)
        self.step += 1
        reward számítás a lépések között


Class StockMarketEnv(gym.Env):

    def __init__(self, kezdő változók):


    def get_observation(self):


    def reset(self):


    def take_action(self, action):


    def step(self, action):


# agent train-elése
model = PPO('MlpPolicy', vec_env, verbose=1)
model.learn(total_timesteps = 1000000)


while not done:
    action, _ = model.predict(obs)
    obs, rewards, done, info = env.step(action)

