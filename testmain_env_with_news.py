import gymnasium.wrappers
from learning import Learning
from backtest import Backtest
from stockmarketenv import StockMarketEnv
from env_with_news import Env_with_news
from handling_models import ModelHandler
from sample_env import SampleEnv




# tanításhoz
# env = Env_with_news('AAPL','2024-03-04','2024-03-15', 100000, 2, '1h', "learn")
# wrapped_env = gymnasium.wrappers.EnvCompatibility(env)
# model = Learning(wrapped_env, steps=10000)



#visszateszteléshez
sample_env = SampleEnv(known_data_number=3)

model_handler = ModelHandler(sample_env)
saved_model = model_handler.choose_model()


env_with_news = Env_with_news('AAPL','2024-04-08', '2024-04-12',100000,2,'1h', "backtest")
Backtest(env = env_with_news, model = saved_model)


