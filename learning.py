from backtest import Backtest
from stockmarketenv import StockMarketEnv
import yfinance as yf
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import DummyVecEnv
import datetime
import os
from handling_models import ModelHandler
from env_with_news import Env_with_news
import torch
from modellstats import ModellStats
from zipfile import ZipFile
from backtest import Backtest
import pandas as pd
import gymnasium as gym
from gymnasium.wrappers import StepAPICompatibility

class Learning():
    def __init__(self, env, steps, getnews, getindexes, getreddit):
        self.env = env
        self.steps = steps
        self.getnews = getnews
        self.getindexes = getindexes
        self.getreddit = getreddit

        self.vec_env = DummyVecEnv([lambda: self.env])
        print('comment from learning: Vektorizálás kész - környezet kész\n')

        self.model = PPO('MlpPolicy', self.vec_env, verbose=1)  # MplpPolicy neural network struktúrával készült, verbose =1 azt jelenti, hogy a console-ra kirak dolgokat a training folyamatáról
        self.model.learn(total_timesteps=self.steps)  # 10 000 akciót hajt végre a trainelés folyamán
        print('comment from learning: Tanulás kész\n')




    def save_model(self):
        if self.getnews == 1 and self.getindexes == 0 and self.getreddit == 0:
            modell_folder_path = r"D:\Egyetem\Diplomamunka\modells\news"


        if self.getnews == 0 and self.getindexes == 0 and self.getreddit == 0:
            modell_folder_path = "D:\Egyetem\Diplomamunka\modells\only prices"


        if self.getnews == 0 and self.getindexes == 1 and self.getreddit == 0:
            modell_folder_path = "D:\Egyetem\Diplomamunka\modells\indexes"


        if self.getnews == 1 and self.getindexes == 1 and self.getreddit == 0:
            modell_folder_path = r"D:\Egyetem\Diplomamunka\modells\news and indexes"


        if self.getnews == 1 and self.getindexes == 0 and self.getreddit == 1:
            modell_folder_path = r"D:\Egyetem\Diplomamunka\modells\news and reddit"


        if self.getnews == 0 and self.getindexes == 0 and self.getreddit == 1:
            modell_folder_path = "D:\Egyetem\Diplomamunka\modells\prices and reddit"


        if self.getnews == 0 and self.getindexes == 1 and self.getreddit == 1:
            modell_folder_path = "D:\Egyetem\Diplomamunka\modells\indexes and reddit"


        if self.getnews == 1 and self.getindexes == 1 and self.getreddit == 1:
            modell_folder_path = r"D:\Egyetem\Diplomamunka\modells\news and indexes and reddit"



        if not os.path.exists(modell_folder_path):
            os.makedirs(modell_folder_path)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        model_filename = f'stock_trading_agent_{timestamp}.zip'
        self.model_joint = os.path.join(modell_folder_path, model_filename)
        self.model.save(self.model_joint)
        print("\n\ncomment from learning: Modell mentése kész\n")




    def getmodel(self):
            saved_model = PPO.load(self.model_joint, env = self.env)
            return saved_model








