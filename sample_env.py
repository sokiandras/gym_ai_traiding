import gymnasium as gym
import numpy as np
import random

class SampleEnv(gym.Env):
    def __init__(self, known_data_number, getnews, getindexes):

        self.known_data_number = known_data_number
        self.getnews = getnews
        self.getindexes = getindexes


        # action space settings
        low_a = np.array([0, 0])
        high_a = np.array([3, 1])
        self.action_space = gym.spaces.Box(low_a, high_a, dtype=np.float32)  # első dimenzió: 0-3 között bármi = 0-1: elad, 1-2: tart, 2-3: vesz;  második dimenzió: 0-1 között bármi = mekkora hányadát költi a pénzének a műveletre.





        # observation space settings
        low_o = 0
        high_o = 1

        if self.getnews == 1 and self.getindexes == 0:
            shape = (7, self.known_data_number)  # így az obs_space úgy fog kinézni, hogy az egyik dimenzió 6 (mivel 6 adatot kap meg a yf által letöltött adatokból - 1 időpontra 6 adat van (high, low, stb.), a másik dimenzió pedig a known_data_number (vagyis azok a sorok amikre visszalát)
            self.observation_space = gym.spaces.Box(low_o, high_o, shape, dtype=np.float32)

        if self.getnews == 0 and self.getindexes == 0:
            shape = (6,self.known_data_number)
            self.observation_space = gym.spaces.Box(low_o, high_o, shape, dtype=np.float32)

        if self.getnews == 0 and self.getindexes == 1:
            shape = (14,self.known_data_number)
            self.observation_space = gym.spaces.Box(low_o, high_o, shape, dtype=np.float32)

        if self.getnews == 1 and self.getindexes == 1:
            shape = (15,self.known_data_number)
            self.observation_space = gym.spaces.Box(low_o, high_o, shape, dtype=np.float32)




