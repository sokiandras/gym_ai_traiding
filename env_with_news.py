import random
import gymnasium as gym
import numpy as np
import yfinance as yf
import datetime
import os
import pandas as pd
from analyze_news import Analyze_news
import openai
import statistics
import graph_maker
from datamaker import DataMaker
from threading import Lock


class Env_with_news(gym.Env):

    def __init__(self, symbol, start_date, end_date, balance, log, data_interval_like_1h, getnews, getindexes, getreddit, usage):
        self.stock_symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.log = log
        self.data_interval = data_interval_like_1h  #így kell kinézni "1h" (STRING!!!)
        self.usage = usage


        #self.current_step = None  # amikor először lefut, akkor még nincs step

        # settings for starting
        self.start_balance = balance  # kezdő egyenleg
        self.known_data_number = 3  # amennyi árat ismer maga előtt
        self.current_step = 0
        self.current_info = 0
        self.current_price = 0
        self.reward = 0
        self.csv_log_file = None

        # points for news analysis
        #self.ai_type = "Gemini"
        self.ai_type = "OpenAI"
        self.getnews = getnews
        self.getindexes = getindexes
        self.getreddit = getreddit

        # action space settings
        low_a = np.array([0, 0])
        high_a = np.array([3, 1])
        self.action_space = gym.spaces.Box(low_a, high_a, dtype=np.float32)  # első dimenzió: 0-3 között bármi = 0-1: elad, 1-2: tart, 2-3: vesz;  második dimenzió: 0-1 között bármi = mekkora hányadát költi a pénzének a műveletre.



        # observation space settings
        low_o = 0
        high_o = 1

        if self.getnews == 1 and self.getindexes == 0 and self.getreddit == 0:
            shape = (7, self.known_data_number)  # így az obs_space úgy fog kinézni, hogy az egyik dimenzió 6 (mivel 6 adatot kap meg a yf által letöltött adatokból - 1 időpontra 6 adat van (high, low, stb.), a másik dimenzió pedig a known_data_number (vagyis azok a sorok amikre visszalát)
            self.observation_space = gym.spaces.Box(low_o, high_o, shape, dtype=np.float32)

        if self.getnews == 0 and self.getindexes == 0 and self.getreddit == 0:
            shape = (6,self.known_data_number)
            self.observation_space = gym.spaces.Box(low_o, high_o, shape, dtype=np.float32)

        if self.getnews == 0 and self.getindexes == 1 and self.getreddit == 0:
            shape = (14,self.known_data_number)
            self.observation_space = gym.spaces.Box(low_o, high_o, shape, dtype=np.float32)

        if self.getnews == 1 and self.getindexes == 1 and self.getreddit == 0:
            shape = (15,self.known_data_number)
            self.observation_space = gym.spaces.Box(low_o, high_o, shape, dtype=np.float32)

        if self.getnews == 1 and self.getindexes == 0 and self.getreddit == 1:
            shape = (8, self.known_data_number)  # így az obs_space úgy fog kinézni, hogy az egyik dimenzió 6 (mivel 6 adatot kap meg a yf által letöltött adatokból - 1 időpontra 6 adat van (high, low, stb.), a másik dimenzió pedig a known_data_number (vagyis azok a sorok amikre visszalát)
            self.observation_space = gym.spaces.Box(low_o, high_o, shape, dtype=np.float32)

        if self.getnews == 0 and self.getindexes == 0 and self.getreddit == 1:
            shape = (7,self.known_data_number)
            self.observation_space = gym.spaces.Box(low_o, high_o, shape, dtype=np.float32)

        if self.getnews == 0 and self.getindexes == 1 and self.getreddit == 1:
            shape = (15,self.known_data_number)
            self.observation_space = gym.spaces.Box(low_o, high_o, shape, dtype=np.float32)

        if self.getnews == 1 and self.getindexes == 1 and self.getreddit == 1:
            shape = (16,self.known_data_number)
            self.observation_space = gym.spaces.Box(low_o, high_o, shape, dtype=np.float32)





        # data in
        self.data_maker()  # itt tölti le az adatokat és egyesíti a hírekkel
        self.stepnumber = len(self.data)


        #logging
        self.log_filename_maker()
        self.step_trade_data = pd.DataFrame(columns=['Step', 'Type', 'Action', 'Possibility', 'Possibility reason', 'Bought pieces', 'Cost', 'Sold pieces', 'Income', 'Total open', 'Total sold', 'Balance', 'Net worth'])
        self.log_frame = pd.DataFrame(columns=['Step', 'Time', 'Current price', 'News', 'Type', 'Action', 'Possibility', 'Possibility reason', 'Bought pieces', 'Cost', 'Sold pieces', 'Income', 'Total open', 'Total sold', 'Balance', 'Net worth', 'Reward'])

        #multithreading
        self.lock = Lock()







    def data_maker(self):
        self.data_class = DataMaker(self.stock_symbol, self.start_date, self.end_date, self.data_interval, self.ai_type, self.getnews, self.getindexes, self.getreddit, self.log)
        self.data_class.data_maker()
        self.data = self.data_class.data







    def get_observation(self):
        # annyi adatsort ismer maga mögött, mint amennyi a a known_data_number

        # normálásokhoz a maximumok
        max_open = self.data['Open'].max()
        max_high = self.data['High'].max()
        max_low = self.data['Low'].max()
        max_close = self.data['Close'].max()
        max_adjclose = self.data['Adj Close'].max()
        max_volume = self.data['Volume'].max()
        max_news_score = 10
        max_reddit_score = 10

        max_ema = None
        max_rsi = None
        max_mom = None
        max_upper_band = None
        max_middle_band = None
        max_lower_band = None
        max_macd = None
        max_macd_signal = None

        if self.getindexes == 1:
            max_ema = self.data['EMA'].max()
            max_rsi = self.data['RSI'].max()
            max_mom = self.data['MOM'].max()
            max_upper_band = self.data['Upper Band'].max()
            max_middle_band = self.data['Middle Band'].max()
            max_lower_band = self.data['Lower Band'].max()
            max_macd = self.data['MACD'].max()
            max_macd_signal = self.data['MACD Signal'].max()


        max_balance = self.start_balance * 100  # ha olyan jó lesz, hogy 1000x-esére növelné a pénzt, akkor ezt át kell írni


        # Common data columns
        base_columns = [
            ('Open', max_open),
            ('High', max_high),
            ('Low', max_low),
            ('Close', max_close),
            ('Adj Close', max_adjclose),
            ('Volume', max_volume)
        ]

        # Optional columns
        news_column = [('News scores', max_news_score)]
        reddit_column = [('Reddit scores', max_reddit_score)]
        indexes_columns = [
            ('EMA', max_ema),
            ('RSI', max_rsi),
            ('MOM', max_mom),
            ('Upper Band', max_upper_band),
            ('Middle Band', max_middle_band),
            ('Lower Band', max_lower_band),
            ('MACD', max_macd),
            ('MACD Signal', max_macd_signal)
        ]

        # Build the frame based on the flags
        columns = base_columns[:]
        if self.getnews:
            columns += news_column
        if self.getreddit:
            columns += reddit_column
        if self.getindexes:
            columns += indexes_columns

        # Create the frame
        frame = np.array([
            self.data.iloc[self.current_step - self.known_data_number: self.current_step][col].values / max_val
            for col, max_val in columns
        ])

        # if self.getnews == 1 and self.getindexes == 0 and self.getreddit == 0:
        #     frame = np.array([
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Open'].values / max_open,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['High'].values / max_high,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Low'].values / max_low,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Close'].values / max_close,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Adj Close'].values / max_adjclose,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Volume'].values / max_volume,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['News scores'].values / max_news_score
        #     ])
        #
        # if self.getnews == 0 and self.getindexes == 0 and self.getreddit == 0:
        #     frame = np.array([
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Open'].values / max_open,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['High'].values / max_high,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Low'].values / max_low,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Close'].values / max_close,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Adj Close'].values / max_adjclose,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Volume'].values / max_volume,
        #     ])
        #
        # if self.getnews == 1 and self.getindexes == 1 and self.getreddit == 0:
        #     frame = np.array([
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Open'].values / max_open,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['High'].values / max_high,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Low'].values / max_low,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Close'].values / max_close,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Adj Close'].values / max_adjclose,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Volume'].values / max_volume,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['News scores'].values / max_news_score,
        #
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['EMA'].values / max_ema,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['RSI'].values / max_rsi,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['MOM'].values / max_mom,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Upper Band'].values / max_upper_band,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Middle Band'].values / max_middle_band,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Lower Band'].values / max_lower_band,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['MACD'].values / max_macd,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['MACD Signal'].values / max_macd_signal
        #     ])
        #
        # if self.getnews == 0 and self.getindexes == 1 and self.getreddit == 0:
        #     frame = np.array([
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Open'].values / max_open,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['High'].values / max_high,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Low'].values / max_low,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Close'].values / max_close,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Adj Close'].values / max_adjclose,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Volume'].values / max_volume,
        #
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['EMA'].values / max_ema,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['RSI'].values / max_rsi,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['MOM'].values / max_mom,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Upper Band'].values / max_upper_band,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Middle Band'].values / max_middle_band,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Lower Band'].values / max_lower_band,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['MACD'].values / max_macd,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['MACD Signal'].values / max_macd_signal
        #     ])
        #
        #
        #
        # if self.getnews == 1 and self.getindexes == 0 and self.getreddit == 1:
        #     frame = np.array([
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Open'].values / max_open,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['High'].values / max_high,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Low'].values / max_low,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Close'].values / max_close,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Adj Close'].values / max_adjclose,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Volume'].values / max_volume,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['News scores'].values / max_news_score,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Reddit scores'].values / max_reddit_score
        #     ])
        #
        # if self.getnews == 0 and self.getindexes == 0 and self.getreddit == 1:
        #     frame = np.array([
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Open'].values / max_open,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['High'].values / max_high,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Low'].values / max_low,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Close'].values / max_close,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Adj Close'].values / max_adjclose,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Volume'].values / max_volume,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Reddit scores'].values / max_reddit_score
        #     ])
        #
        # if self.getnews == 1 and self.getindexes == 1 and self.getreddit == 1:
        #     frame = np.array([
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Open'].values / max_open,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['High'].values / max_high,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Low'].values / max_low,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Close'].values / max_close,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Adj Close'].values / max_adjclose,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Volume'].values / max_volume,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['News scores'].values / max_news_score,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Reddit scores'].values / max_reddit_score,
        #
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['EMA'].values / max_ema,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['RSI'].values / max_rsi,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['MOM'].values / max_mom,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Upper Band'].values / max_upper_band,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Middle Band'].values / max_middle_band,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Lower Band'].values / max_lower_band,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['MACD'].values / max_macd,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['MACD Signal'].values / max_macd_signal
        #     ])
        #
        # if self.getnews == 0 and self.getindexes == 1 and self.getreddit == 1:
        #     frame = np.array([
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Open'].values / max_open,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['High'].values / max_high,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Low'].values / max_low,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Close'].values / max_close,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Adj Close'].values / max_adjclose,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Volume'].values / max_volume,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Reddit scores'].values / max_reddit_score,
        #
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['EMA'].values / max_ema,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['RSI'].values / max_rsi,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['MOM'].values / max_mom,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Upper Band'].values / max_upper_band,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Middle Band'].values / max_middle_band,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['Lower Band'].values / max_lower_band,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['MACD'].values / max_macd,
        #         self.data.iloc[self.current_step - self.known_data_number: self.current_step]['MACD Signal'].values / max_macd_signal
        #     ])




        if self.log == 2 or self.log == 3:
            print('\n\n Observation frame:')
            print(frame)
            print('\n')

        observation = frame

        return observation







    def reset(self):
        #self.current_step = self.known_data_number + 1
        self.current_step = self.known_data_number
        self.balance = self.start_balance
        self.net_worth = self.start_balance
        # self.prev_balance = self.start_balance
        self.total_reward = 0
        self.total_profit = 0

        # arra vonatkozik, hogy hány részvény db-ot vettünk/eladtunk összesen (ha 100 db apple részvényt vettünk, akkor itt 100 db fog látszódni)
        self.total_bought_open = 0
        self.total_bought_closed = 0
        self.total_shorted_open = 0
        self.total_shorted_closed = 0
        self.sales_log = []

        # a jövőben arra fog vonatkozni, hogy milyen fajta részvénnyel történt. pl. ha apple-ből veszünk 100 db-ot, akkor itt 1 db apple jelenik meg
        self.share_bought_open = 0
        self.share_bought_closed = 0
        self.share_shorted_open = 0
        self.share_shorted_closed = 0


        return self.get_observation()






    def take_action(self, action):
        action_type = action[0]
        balance_usage_ratio = action[1]
        sell_ratio = action[1]
        self.current_price = 0


        open_price = self.data.iloc[self.current_step]['Open']
        close_price = self.data.iloc[self.current_step]['Close']
        self.current_price = random.uniform(open_price, close_price)  # az adott lépésnél az Open és a Close ár között választ egy véletlen árat
        self.prev_net_worth = self.net_worth


        if action_type <= 1:  # vásárlás  (annyi darabot, ahányad részét a balance_usage_ratio enged)
            type = 'Buy'
            if (balance_usage_ratio == 0):
                possibility = 0
                possibility_reason = 'Buy, but balance_usage_ration = 0'
                self.net_worth = self.balance + self.total_bought_open * self.current_price
                self.current_info = {
                    'step: ': self.current_step,
                    'possibility: ': possibility,
                    'possibility reason: ': possibility_reason,
                }
                self.step_trade_data_appender(type, action, possibility, possibility_reason, 0, 0, 0, 0)
                pass
            else:
                possible_number_of_boughts = (self.balance * balance_usage_ratio / self.current_price) // 1  # ennyi darabot lehet max venni (a //1 az alsó egészrész
                if (possible_number_of_boughts > 0):
                    possibility = 1
                    self.total_bought_open = self.total_bought_open + possible_number_of_boughts
                    additional_cost = possible_number_of_boughts * self.current_price
                    self.balance = self.balance - additional_cost
                    self.net_worth = self.balance + self.total_bought_open * self.current_price
                    self.current_info = {
                        'step: ': self.current_step,
                        'type: ': type,
                        'possibility: ': possibility,
                        'bought pieces: ': possible_number_of_boughts,
                        'current price ': self.current_price,
                        'cost: ': additional_cost,
                    }
                    self.step_trade_data_appender(type, action, possibility, 0, possible_number_of_boughts, additional_cost, 0, 0)
                    pass
                else:
                    possibility = 0
                    possibility_reason = 'Buy, but possible number of boughts = 0'
                    self.net_worth = self.balance + self.total_bought_open * self.current_price
                    self.current_info = {
                        'step: ': self.current_step,
                        'type: ': type,
                        'possibility: ': possibility,
                        'possibility reason: ': possibility_reason,
                    }
                    self.step_trade_data_appender(type, action, possibility, possibility_reason, 0, 0, 0, 0)
            pass


        elif action_type > 1 and action_type <= 2:  # hold
            type = 'hold'
            possibility = 1
            self.net_worth = self.balance + self.total_bought_open * self.current_price
            self.current_info = {
                'step: ': self.current_step,
                'type: ': type,
            }
            self.step_trade_data_appender(type, action, possibility, 0, 0, 0, 0, 0, )
            pass


        elif action_type > 2 and action_type <= 3:  # elad (annyi darabot, ahányad részt megad a sell_ratio)
            type = 'sell'
            if (sell_ratio == 0):
                possibility = 0
                possibility_reason = 'Sell, but sell_ration = 0'
                self.net_worth = self.balance + self.total_bought_open * self.current_price
                self.current_info = {
                    'step: ': self.current_step,
                    'possibility: ': possibility,
                    'possibility reason: ': possibility_reason,
                }
                self.step_trade_data_appender(type, action, possibility, possibility_reason, 0, 0, 0, 0)
                pass
            else:
                possible_number_of_sells = (self.total_bought_open * sell_ratio) // 1  # ennyi darabot ad el
                type = 'sell'
                if (possible_number_of_sells > 0):
                    possibility = 1
                    self.total_bought_closed = self.total_bought_closed + possible_number_of_sells
                    self.total_bought_open = self.total_bought_open - possible_number_of_sells
                    additional_income = self.current_price * possible_number_of_sells
                    self.balance = self.balance + additional_income
                    self.net_worth = self.balance + self.total_bought_open * self.current_price
                    self.current_info = {
                        'step: ': self.current_step,
                        'type: ': type,
                        'possibility: ': possibility,
                        'sold pieces: ': possible_number_of_sells,
                        'current price ': self.current_price,
                        'income: ': additional_income,
                    }
                    self.step_trade_data_appender(type, action, possibility, 0, 0, 0, possible_number_of_sells, additional_income)
                    pass
                else:
                    possibility = 0
                    possibility_reason = 'Sell, but possible number of sells = 0'
                    self.net_worth = self.balance + self.total_bought_open * self.current_price
                    self.current_info = {
                        'step: ': self.current_step,
                        'type: ': type,
                        'possibility: ': possibility,
                        'possibility reason: ': possibility_reason,
                    }
                    self.step_trade_data_appender(type, action, possibility, possibility_reason, 0, 0, 0, 0)
            pass


        elif (action[0] == 0 and action[1] == 0):
            type = 'action[0 0]'
            possibility = 0
            possibility_reason = 'action = [0 0]'
            self.net_worth = self.balance + self.total_bought_open * self.current_price
            self.current_info = {
                'step: ': self.current_step,
                'possibility: ': possibility,
                'possibility reason: ': possibility_reason
            }
            self.step_trade_data_appender(type, action, possibility, possibility_reason, 0, 0, 0, 0)




        self.current_info['total open shares: '] = self.total_bought_open
        self.current_info['total sold shares so far: '] = self.total_bought_closed
        self.current_info['current balance: '] = self.balance
        # self.net_worth = self.balance + self.total_bought_open * self.current_price
        self.current_info['current net worth: '] = self.net_worth
        self.current_info['action: '] = action

        if self.current_info:
            self.sales_log.append(self.current_info)



        return self.current_info



    def step_trade_data_appender(self, type, action, possibility, possibility_reason, bought_pieces, cost, sold_pieces, income):
        self.step_trade_data = self.step_trade_data._append({
            'Step': self.current_step,
            'Type': type,
            'Action': action,
            'Possibility': possibility,
            'Possibility reason': possibility_reason,
            'Bought pieces': bought_pieces,
            'Cost': cost,
            'Sold pieces': sold_pieces,
            'Income': income,
            'Total open': self.total_bought_open,
            'Total sold': self.total_bought_closed,
            'Balance': self.balance,
            'Net worth': self.net_worth
        }, ignore_index=True)






    def step(self, action):

        time = self.data.index[self.current_step]
        if (self.log):
            print(time)  # csak azért, hogy külön sorba írja

        current_info = self.take_action(action)
        if (self.log):
            print(current_info)  # minden step current infoja (kivéve time és profit)

        self.reward = self.net_worth - self.prev_net_worth
        if (self.log):
            print(f'Reward (profit of the step): {self.reward} \n')  # csak azért van így, hogy külön sorba írja ki, így látványosabb legyen a profit

        self.current_info['Reward = Profit: '] = self.reward
        self.current_info['Time: '] = time

        if self.usage == "backtest":
            self.log_one_step_for_csv()

        with self.lock:
            self.current_step = self.current_step + 1


        done = False
        #if (self.current_step + 1 == len(self.data)):
        if (self.current_step == len(self.data)):
            done = True
            total_profit = self.net_worth - self.start_balance
            print('comment from env: Last step on dataline')
            total_profit_to_log = {'Total profit: ', total_profit}
            print('comment from env: Total profit: ', total_profit)
            self.sales_log.append(total_profit_to_log)
            print('comment from env: data length: ', len(self.data))
            self.save_txt_and_csv_logs()

        observations = self.get_observation()


        return observations, self.reward, done, current_info




    def log_one_step_for_csv(self):
        step_data_index = self.current_step - self.known_data_number
        #step_data_index = self.current_step - self.known_data_number -1
        if (self.log == 3):
            print('\nlog_one_step_for_csv()')
            print(f'\nself.current_step = {self.current_step} step_data_index = {step_data_index} len(self.step_data) = {len(self.step_trade_data)} message from log_one_step_for_csv()')



        log_frame_base = {
            'Step': self.current_step,
            'Time': self.data.index[self.current_step],
            'Current price': self.current_price,
            'Type': self.step_trade_data.iloc[step_data_index]['Type'],
            'Action': self.step_trade_data.iloc[step_data_index]['Action'],
            'Possibility': self.step_trade_data.iloc[step_data_index]['Possibility'],
            'Possibility reason': self.step_trade_data.iloc[step_data_index]['Possibility reason'],
            'Bought pieces': self.step_trade_data.iloc[step_data_index]['Bought pieces'],
            'Cost': self.step_trade_data.iloc[step_data_index]['Cost'],
            'Sold pieces': self.step_trade_data.iloc[step_data_index]['Sold pieces'],
            'Income': self.step_trade_data.iloc[step_data_index]['Income'],
            'Total open': self.step_trade_data.iloc[step_data_index]['Total open'],
            'Total sold': self.step_trade_data.iloc[step_data_index]['Total sold'],
            'Balance': self.step_trade_data.iloc[step_data_index]['Balance'],
            'Net worth': self.step_trade_data.iloc[step_data_index]['Net worth'],
            'Reward': self.reward,
        }




        if self.getnews == 1:
            log_frame_base.update({
                'News': self.data.iloc[self.current_step]['News scores'],
                'News URLs': self.data.iloc[self.current_step]['News URLs'],
            })


        if self.getindexes == 1:
            log_frame_base.update({
                'EMA': self.data.iloc[self.current_step]['EMA'],
                'RSI': self.data.iloc[self.current_step]['RSI'],
                'MOM': self.data.iloc[self.current_step]['MOM'],
                'Upper Band': self.data.iloc[self.current_step]['Upper Band'],
                'Middle Band': self.data.iloc[self.current_step]['Middle Band'],
                'Lower Band': self.data.iloc[self.current_step]['Lower Band'],
                'MACD': self.data.iloc[self.current_step]['MACD'],
                'MACD Signal': self.data.iloc[self.current_step]['MACD Signal']
            })

        if self.getreddit == 1:
            log_frame_base.update({
                'Reddit scores': self.data.iloc[self.current_step]['Reddit scores']
            })

        self.log_frame = self.log_frame._append(log_frame_base, ignore_index=True)


        # else:
        #     print('\nStep data index is out of the range of len(self.step_data')




    def close(self):
        print('Close')



    def log_filename_maker(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        if self.usage == "learn":
            self.log_filename = f'learning_log_{timestamp}.txt'
            self.csv_filename = f'learning_log_{timestamp}.csv'
            self.excel_filename = f'learning_log_{timestamp}.xlsx'
        elif self.usage == "backtest":
            self.log_filename = f'backtest_log_{timestamp}.txt'
            self.csv_filename = f'backtest_log_{timestamp}.csv'
            self.excel_filename = f'backtest_log_{timestamp}.xlsx'




    def save_txt_and_csv_logs(self):

        if self.usage == "learn":
            log_folder_path = "D:\Egyetem\Diplomamunka\logs\Learnings"
            if not os.path.exists(log_folder_path):
                os.makedirs(log_folder_path)
            opening_method = "a"

        elif self.usage == "backtest":
            log_folder_path = "D:\Egyetem\Diplomamunka\logs\Backtests"
            if not os.path.exists(log_folder_path):
                os.makedirs(log_folder_path)
            opening_method = "x"

            csv_file = os.path.join(log_folder_path, self.csv_filename)
            self.log_frame.to_csv(csv_file)

            excel_file = os.path.join(log_folder_path, self.excel_filename)
            self.log_frame.to_excel(excel_file)

            graph_maker.make_graph(csv_file)

        else:
            print("\nUncorrect usage type for log saving (message from save_txt_and_csv_logs()")
            return -1


        logfile = os.path.join(log_folder_path, self.log_filename)
        with open(logfile, opening_method) as file:
            for i in self.sales_log:
                file.write('%s\n\n' % i)



        return 0






# test_env = Env_with_news('AAPL','2024-03-19', '2024-03-19',100000,2,'1h', 'backtest')
# test_env.better_news_analysis_in_given_interval()
# test_env.set_datetime_index_for_news_scores()
# test_env.set_datetime_index_for_news_urls()
#test_env.give_as_many_news_scores_as_dataline()

#test_env = Env_with_news('AAPL','2024-09-23', '2024-09-24',100000,2,'1h', 1, 1, 1, 'backtest')

