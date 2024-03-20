import pandas as pd
from stockmarketenv import StockMarketEnv
from stable_baselines3.common.env_util import DummyVecEnv
import yfinance as yf
import datetime
import numpy as np



class Backtest():
    def __init__(self, model, env, log=True):
        self.model = model
        self.env = env
        print('comment from backtest: Model recieved: ', self.model)


        observation = self.env.reset()
        done = False

        while not done:
            action, _ = self.model.predict(observation)
            obs, rewards, done, info = self.env.step(action)  # env.step([action])

            if done:
                #self.env.save_txt_and_csv_logs()
                obs = self.env.reset()
                print('\nEnd testing on dataset (message from Backtest())')
                print('\nlog saved succesfully (message from Backtest())')

