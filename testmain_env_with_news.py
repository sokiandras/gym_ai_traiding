import gymnasium.wrappers
from learning import Learning
from backtest import Backtest
from stockmarketenv import StockMarketEnv
from env_with_news import Env_with_news
from handling_models import ModelHandler
from sample_env import SampleEnv


getnews = 0  # 1: environment with news, 0: environment without news
getindexes = 0
learning = 0



# tanításhoz
if learning == 1:
    env = Env_with_news('AAPL','2024-03-25','2024-04-05', 100000, 2, '1h', getnews, getindexes, "learn")
    wrapped_env = gymnasium.wrappers.EnvCompatibility(env)
    model = Learning(wrapped_env, 10000, getnews)




#visszateszteléshez
sample_env = SampleEnv(known_data_number=3, getnews=getnews)

model_handler = ModelHandler(sample_env, getnews)
saved_model = model_handler.choose_model()


env_with_news = Env_with_news('AAPL','2024-04-08', '2024-04-10',100000,2,'1h', getnews, getindexes, "backtest")
Backtest(env = env_with_news, model = saved_model)


