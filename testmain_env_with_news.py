import gymnasium.wrappers
from learning import Learning
from backtest import Backtest
from stockmarketenv import StockMarketEnv
from env_with_news import Env_with_news
from handling_models import ModelHandler
from sample_env import SampleEnv


getnews = 0  # 1: environment with news, 0: environment without news
getindexes = 1

learning = 0



# tanításhoz
if learning == 1:
    env = Env_with_news('GOOGL','2024-04-08','2024-04-10', 100000, 2, '1h', getnews, getindexes, "learn")
    wrapped_env = gymnasium.wrappers.EnvCompatibility(env)
    learn = Learning(wrapped_env, 10000, getnews, getindexes)
    learn.save_model()




#visszateszteléshez
sample_env = SampleEnv(known_data_number=3, getnews=getnews, getindexes=getindexes)

model_handler = ModelHandler(sample_env, getnews, getindexes)
saved_model = model_handler.choose_model()


env_with_news = Env_with_news('GOOGL','2024-04-17', '2024-04-19',100000,2,'1h', getnews, getindexes, "backtest")
Backtest(env = env_with_news, model = saved_model)


