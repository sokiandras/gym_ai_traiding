from learning import Learning
from backtest import Backtest
from stockmarketenv import StockMarketEnv



env = StockMarketEnv(symbol='AAPL', start_date='2022-01-01', end_date='2022-04-26', balance=100000, log=True)
model = Learning(env, steps=10000)

print("\ncomment from main: A tanulási folyamat kész van\n")

saved_model = model.getmodel()

env2 = StockMarketEnv(symbol='AAPL', start_date='2022-04-01', end_date='2022-08-26', balance=100000,log=False)

Backtest(env = env2, model = saved_model)

env3 = StockMarketEnv(symbol='AAPL', start_date='2022-09-01', end_date='2022-12-26', balance=100000,log=False)
Backtest(env = env3, model = saved_model)



