import yfinance as yf
from stockmarketenv import StockMarketEnv
import gym
import numpy as np
from stable_baselines3 import PPO
#from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.env_util import DummyVecEnv
import datetime
import os
from modellstats import ModellStats
from zipfile import ZipFile
from backtest import Backtest
from learning import Learning
import pandas as pd
#--------------------------------------------------------------------------------------------


# környezet elkészítése és vektorizálása
env = StockMarketEnv(symbol='AAPL', start_date='2022-01-01', end_date='2022-04-26', balance=100000, log=False)
vec_env = DummyVecEnv([lambda: env])
print('Vektorizálás kész - környezet kész\n')



# agent train-elése
model = PPO('MlpPolicy', vec_env, verbose=1)  # MplpPolicy neural network struktúrával készült, verbose =1 azt jelenti, hogy a console-ra kirak dolgokat a training folyamatáról
model.learn(total_timesteps = 1000)   # 10 000 akciót hajt végre a trainelés folyamán
print('Tanulás kész\n')



# modell mentése
modell_folder_path = "D:\Egyetem\Önlab\sajat1\modells"
if not os.path.exists(modell_folder_path):
    os.makedirs(modell_folder_path)
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
model_filename = f'stock_trading_agent_{timestamp}.zip'
model_joint = os.path.join(modell_folder_path, model_filename)
model.save(model_joint)

saved_model = PPO.load(model_joint, env = env)

#model.save(f'stock_trading_agent_{timestamp}.zip')



# környezet beállítása a teszteléshez
obs = env.reset()
done = False

print('comment from backtest: Model recieved: ', saved_model)

# visszatesztelés ugyanazon az adatsoron
print("\nTesting on the same dataset")
while not done:
    action, _ = saved_model.predict(obs)
    #action, _ = model.predict(obs)
    obs, rewards, done, info = env.step(action)     # env.step([action])

    if done:
        env.log_writer()
        obs = env.reset()
        print('End testing on same dataset')
        print('log saved succesfully')



# visszatesztelés másik adatsoron
print('\nTesting on different dataset')
env2 = StockMarketEnv(symbol='AAPL', start_date='2022-04-01', end_date='2022-08-26', balance=100000, log = False)
vec_env2 = DummyVecEnv([lambda: env2])

obs2 = env2.reset()
done = False

while not done:
    action, _ = saved_model.predict(obs2)
    #action, _ = model.predict(obs2)
    obs2, rewards, done, info = env2.step(action)     # env.step([action])

    if done:
        env2.log_writer()
        obs2 = env2.reset()
        print('End testing on different dataset')
        print('log saved succesfully')






# Modell bias-ai és weights-ei:
print('Modell stats: ')

extract_folder_name = f"extracted_{timestamp}"
extract_path = "D:\Egyetem\Önlab\sajat1\modells"
where_to_extract = os.path.join(extract_path, extract_folder_name)
os.makedirs(where_to_extract)


current_model_zip_path = os.path.join(modell_folder_path, model_filename)
with ZipFile(current_model_zip_path, 'r') as zip_file:
    zip_file.extractall(where_to_extract)

interested_filename = 'policy.optimizer.pth'
interested_file_path = os.path.join(where_to_extract, interested_filename)
model = ModellStats(interested_file_path)
#model.weights_and_biases()
