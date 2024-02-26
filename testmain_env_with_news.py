from learning import Learning
from backtest import Backtest
from stockmarketenv import StockMarketEnv
from env_with_news import Env_with_news



env = Env_with_news('AAPL','2024-01-25','2024-01-30', 100000, 2, '1h')
model = Learning(env, steps=10000)

saved_model = model.getmodel()

env_with_news = Env_with_news('AAPL','2024-01-31', '2024-02-15',100000,2,'1h')
Backtest(env = env_with_news, model = saved_model)


