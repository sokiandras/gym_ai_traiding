from learning import Learning
from backtest import Backtest
from stockmarketenv import StockMarketEnv
from env_with_news import Env_with_news



env_for_learning = Env_with_news('AAPL','2023-11-13','2023-12-01', 100000, 2, '1h')
model = Learning(env_for_learning, steps=10000)

saved_model = model.getmodel()

env_for_backtest = Env_with_news('AAPL','2023-12-02', '2023-12-11',100000,2,'1h')
Backtest(env = env_for_backtest, model = saved_model)


