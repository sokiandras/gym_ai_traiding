import gymnasium.wrappers
from learning import Learning
from backtest import Backtest
from stockmarketenv import StockMarketEnv
from env_with_news import Env_with_news
from handling_models import ModelHandler
from sample_env import SampleEnv


getnews = 0  # 1: environment with news, 0: environment without news
getindexes = 1
getreddit = 1

learning = 0


# tanításhoz
if learning == 1:
    env = Env_with_news('AAPL','2024-09-19','2024-09-20', 100000, 2, '1h', getnews, getindexes, getreddit, "learn")
    wrapped_env = gymnasium.wrappers.EnvCompatibility(env)
    learn = Learning(wrapped_env, 10000, getnews, getindexes, getreddit)
    learn.save_model()



#visszateszteléshez
sample_env = SampleEnv(known_data_number=3, getnews=getnews, getindexes=getindexes, getreddit=getreddit)

model_handler = ModelHandler(sample_env, getnews, getindexes, getreddit)
saved_model = model_handler.choose_model()


env_with_news = Env_with_news('AAPL','2024-09-23', '2024-09-24',100000,2,'1h', getnews, getindexes, getreddit, "backtest")
Backtest(env = env_with_news, model = saved_model)


