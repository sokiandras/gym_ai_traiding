from learning import Learning
from backtest import Backtest
from stockmarketenv import StockMarketEnv
import gymnasium as gym
from gymnasium.envs.registration import register




register(
    id="StockMarketEnv-v1",
    entry_point="stockmarketenv:StockMarketEnv",
    max_episode_steps=20000,
    reward_threshold=500
)

env=gym.make("StockMarketEnv-v1", apply_api_compatibility=True, **{"symbol": "AAPL", "start_date": "2023-01-01", "end_date": "2023-04-26", "balance": 100000, "log": True})

model = Learning(env, steps=10000)

print("\ncomment from main: A tanulási folyamat kész van\n")

saved_model = model.getmodel()

env2 = StockMarketEnv(symbol='AAPL', start_date='2023-04-01', end_date='2023-08-26', balance=100000,log=False)

Backtest(env = env2, model = saved_model)

env3 = StockMarketEnv(symbol='AAPL', start_date='2023-09-01', end_date='2023-12-26', balance=100000,log=False)
Backtest(env = env3, model = saved_model)



