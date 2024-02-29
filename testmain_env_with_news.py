from learning import Learning
from backtest import Backtest
from stockmarketenv import StockMarketEnv
from env_with_news import Env_with_news
import gymnasium as gym
from gymnasium.envs.registration import register



register(
    id="StockMarketEnv_with_news-v1",
    entry_point="env_with_news:Env_with_news",
    max_episode_steps=20000,
    reward_threshold=500
)

#env = Env_with_news('AAPL','2024-02-10','2024-02-20', 100000, 2, '1h')
env=gym.make("StockMarketEnv_with_news-v1", apply_api_compatibility=True, symbol="AAPL", start_date="2024-02-17", end_date="2024-02-20", balance=100000, log=2, data_interval_like_1h='1h')
model = Learning(env, steps=10000)

saved_model = model.getmodel()

env_with_news = Env_with_news('AAPL','2024-02-21', '2024-02-24',100000,2,'1h')
Backtest(env = env_with_news, model = saved_model)


