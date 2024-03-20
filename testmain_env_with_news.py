import gymnasium.wrappers

from learning import Learning
from backtest import Backtest
from stockmarketenv import StockMarketEnv
from env_with_news import Env_with_news
from handling_models import ModelHandler



# register(
#     id="StockMarketEnv_with_news-v1",
#     entry_point="env_with_news:Env_with_news",
#     max_episode_steps=20000,
#     reward_threshold=500
# )
#
# wrapped_env=gym.make("StockMarketEnv_with_news-v1", apply_api_compatibility=True, symbol="AAPL", start_date="2024-03-01", end_date="2024-03-03", balance=100000, log=2, data_interval_like_1h='1h', usage="learn")


env = Env_with_news('AAPL','2024-03-04','2024-03-06', 100000, 2, '1h', "learn")
wrapped_env = gymnasium.wrappers.EnvCompatibility(env)
# model = Learning(wrapped_env, steps=10000)
#
# saved_model = model.getmodel()

model_handler = ModelHandler(env)
model_handler.choose_model()
saved_model = model_handler.get_model()

env_with_news = Env_with_news('AAPL','2024-03-11', '2024-03-13',100000,2,'1h', "backtest")
Backtest(env = env_with_news, model = saved_model)


