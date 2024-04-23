import yfinance as yf
import pandas as pd
import datetime
import openai
import statistics
from analyze_news import Analyze_news
from alpha_vantage.techindicators import TechIndicators
import sys
from alpha_vantage.timeseries import TimeSeries
import requests
from yahoo_fin.stock_info import get_quote_table, get_data


class DataMaker():
    def __init__(self, symbol, start_date, end_date, data_interval, ai_type, getnews, getindexes, log):
        self.stock_symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.data_interval = data_interval
        self.ai_type = ai_type
        self.getnews = getnews
        self.getindexes = getindexes
        self.log = log

        self.analyzing_times = []
        self.counter_for_analyzed_hours = 0
        self.reducated_news_urls = []
        self.news_scores = []
        self.news_scores_with_index = pd.DataFrame
        self.reducated_news_scores = pd.DataFrame





    def yf_downloader(self):
        try:
            self.data = yf.download(self.stock_symbol, self.start_date, self.end_date, interval=self.data_interval)
        except Exception as e:
            print(f'Error with downloading data from Yahoo Finance: {e}')
            return -1
        if self.data is None or self.data.empty:
            print("No data was downloaded from yahoo finance. Exiting the program.")
            raise SystemExit("No data was downloaded from yahoo finance. Exiting the program.")
        if self.log == 2 or self.log == 3:
            print("Original Yahoo finance data: from yf_downloader()\n")
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            print(self.data)
            pd.reset_option('display.max_rows')
            pd.reset_option('display.max_columns')



    def better_news_analysis_in_given_interval(self):

        start_date = datetime.datetime.strptime(self.start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(self.end_date, "%Y-%m-%d")
        current_date = start_date

        date_delta = datetime.timedelta(days=1)
        self.news_urls = [[]]

        while current_date <= end_date:
            news_analyzer = Analyze_news(self.stock_symbol, current_date, self.ai_type, self.analyzing_times, self.log)
            news_analyzer.get_news_for_a_day()
            current_date_string = current_date.strftime("%Y-%m-%d")

            for current_hour in range(24):
                hourly_urls = []
                try:
                    average_score, hourly_urls = news_analyzer.analyze_for_an_hour(current_hour)
                except openai.error.InvalidRequestError as e:
                    if self.log <= 3:
                        print(f"\nError occurred while analyzing news: {str(e)} news details: {current_date}, hour: {current_hour}")
                        print("\nSkipping this news and continuing with the next one.")
                        average_score = -1
                        current_date += date_delta

                if self.log <= 3:
                    print(f"\nAnalysis for {current_date_string} - hour: {current_hour} - result score: {average_score} (message from better_news_analysis_in_given_interval())")

                if average_score != -1:
                    self.news_scores.append(average_score)


                else:
                    self.news_scores.append(5)

                self.news_urls[self.counter_for_analyzed_hours].extend(hourly_urls)
                #self.news_urls.append(hourly_hours)
                self.news_urls.append([])
                self.counter_for_analyzed_hours = self.counter_for_analyzed_hours + 1



            current_date += date_delta

            #self.news_urls.append([])

        print(f"\n\n\nNews scores between {self.start_date} and {self.end_date}: {self.news_scores} (better_news_analysis_in_given_interval())")



    def set_datetime_index_for_data(self):
        string_index = self.data.index.strftime('%Y-%m-%d %H')
        datetime_index = pd.to_datetime(string_index)
        self.data.index = datetime_index

        if self.log == 3:
            print('\ndata: from set_datetime_index_for_data()\n')
            print(self.data)




    def set_datetime_index_for_news_scores(self):
        news_scores_with_index = pd.Series(self.news_scores)

        datetime_strings = []
        current_date = datetime.datetime.strptime(self.start_date, "%Y-%m-%d")
        interval_in_int = int(self.data_interval[:-1])

        if self.data_interval.endswith('h'):
            delta = datetime.timedelta(hours=interval_in_int)
        elif self.data_interval.endswith('d'):
            delta = datetime.timedelta(days=interval_in_int)

        while len(datetime_strings) < len(news_scores_with_index):
            current_hour = current_date.strftime("%H")
            current_date_string = current_date.strftime("%Y-%m-%d")
            datetime_strings.append(f"{current_date_string} {current_hour}")
            current_date += delta

        index_in_datetime = pd.to_datetime(datetime_strings)
        news_scores_with_index.index = index_in_datetime

        self.news_scores_with_index = news_scores_with_index

        if self.log <= 3:
            print(f"\nNews score in indexed series: (message from set_datetime_index_for_news_scores())\n ", self.news_scores_with_index)




    def set_datetime_index_for_news_urls(self):
        news_urls_with_index = {}

        datetime_strings = []
        current_date = datetime.datetime.strptime(self.start_date, "%Y-%m-%d")
        interval_in_int = int(self.data_interval[:-1])

        if self.data_interval.endswith('h'):
            delta = datetime.timedelta(hours=interval_in_int)
        elif self.data_interval.endswith('d'):
            delta = datetime.timedelta(days=interval_in_int)

        for urls in self.news_urls:
            current_hour = current_date.strftime("%H")
            current_date_string = current_date.strftime("%Y-%m-%d")
            datetime_strings.append(f"{current_date_string} {current_hour}")
            current_date += delta

        for i, datetime_string in enumerate(datetime_strings):
            news_urls_with_index[datetime_string] = self.news_urls[i]

        self.news_urls_with_index = news_urls_with_index

        if self.log <= 3:
            print(f"\nNews URLs in indexed dictionary: (message from set_datetime_index_for_news_urls())\n ",
                  self.news_urls_with_index)



    def give_as_many_news_scores_and_urls_as_dataline(self):
        self.set_datetime_index_for_data()
        self.set_datetime_index_for_news_scores()
        self.set_datetime_index_for_news_urls()

        new_scores = []
        temp_scores = []

        new_urls = []
        temp_urls = []

        self.data.index = self.data.index.strftime('%Y-%m-%d %H')
        self.news_scores_with_index.index = self.news_scores_with_index.index.strftime('%Y-%m-%d %H')

        for index in self.news_scores_with_index.index:

            if index in self.data.index:
                if temp_scores:  # if temp_scores is not empty
                    temp_scores.append(self.news_scores_with_index.loc[index])
                    average_score = sum(temp_scores) / len(temp_scores)
                    score = average_score
                    temp_scores = []  # reset temp_scores
                else:
                    score = self.news_scores_with_index.loc[index]

                new_scores.append(score)
            else:
                temp_scores.append(self.news_scores_with_index.loc[index])

        self.reducated_news_scores = pd.Series(new_scores, index=self.data.index)

        if self.log <= 3:
            print("\n\nReducated news scores list: (message from give_as_many_news_scores_as_dataline())",
                  self.reducated_news_scores)



        for index in self.news_urls_with_index:
            #average_url_list = []
            if index in self.data.index:
                if temp_urls:  # Check if temp_urls has any accumulated URLs
                    # temp_urls.append(self.news_urls_with_index[index])
                    temp_urls.extend(self.news_urls_with_index[index])
                    average_url_list = temp_urls  # Since URLs are not scores, use entire list
                    temp_urls = []  # Reset temp_urls
                else:
                    average_url_list = self.news_urls_with_index[index]

                new_urls.append(average_url_list)  # Append list of URLs for the data point

            #ez új:
            else:
                temp_urls.extend(self.news_urls_with_index[index])


        self.reducated_news_urls = new_urls  # No need for Series as URLs aren't scores
        if self.log <= 3:
            print("\n\nReducated news URLs list: (message from give_as_many_news_urls_as_dataline())",
                  self.reducated_news_urls)








    def sma(self):  #only to see how it looks like without mapping
        sma, _ = self.tech_indicators.get_sma(symbol='AAPL', interval='60min', time_period=20, series_type='close')
        sma = sma.reindex(self.date_range)
        sma = sma.dropna()
        sma.index = sma.index.strftime('%Y-%m-%d %H')
        sma, self.data = sma.align(self.data, axis=0, join='inner')

        print('\nSMA values:')
        pd.set_option('display.max_rows', None)
        print(sma)
        pd.reset_option('display.max_rows')






    def get_one_indicator(self, indicator_name):
        # Map the indicator names to the corresponding functions
        indicators = {
            'sma': self.tech_indicators.get_sma,
            'ema': self.tech_indicators.get_ema,
            'kama': self.tech_indicators.get_kama,
            'rsi': self.tech_indicators.get_rsi,
            'mom': self.tech_indicators.get_mom,
            'stoch': self.tech_indicators.get_stoch,
            'stochf': self.tech_indicators.get_stochf,
            'bbands': self.tech_indicators.get_bbands,
            'macdext': self.tech_indicators.get_macdext
        }

        # Get the function for the specified indicator
        indicator_func = indicators.get(indicator_name)

        if indicator_func is None:
            raise ValueError(f'Invalid indicator name: {indicator_name}')

        # Call the function and process the result
        if indicator_name == 'stoch' or 'stochf': #a stoch-hoz nem kell time period
            try:
                indicator, _ = indicator_func(symbol='AAPL', interval='60min')
            except ValueError as e:
                print(f'Hiba történt az indikátor letöltése közben: {e}, kilépés a programból')
                sys.exit()
        else:
            try:
                indicator, _ = indicator_func(symbol='AAPL', interval='60min', time_period=20, series_type='close')
            except ValueError as e:
                print(f'Hiba történt az indikátor letöltése közben: {e}, kilépés a programból')
                sys.exit()


        indicator = indicator.reindex(self.date_range)
        indicator = indicator.dropna()
        indicator.index = indicator.index.strftime('%Y-%m-%d %H')
        indicator, self.data = indicator.align(self.data, axis=0, join='inner')

        if self.log == 3:
            print(f'\n{indicator_name.upper()} values:')
            pd.set_option('display.max_rows', None)
            print(indicator)
            pd.reset_option('display.max_rows')

        return indicator



    def indexes(self):
        self.av_api_key = open("AlphaVentage_API_KEY.txt", "r").read()
        self.tech_indicators = TechIndicators(key=self.av_api_key, output_format='pandas')
        self.date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='h')

        self.data['EMA'] = self.get_one_indicator('ema')['EMA']
        self.data['RSI'] = self.get_one_indicator('rsi')['RSI']
        self.data['MOM'] = self.get_one_indicator('mom')['MOM']

        bbands = self.get_one_indicator('bbands')
        self.data['Upper Band'] = bbands['Real Upper Band']
        self.data['Middle Band'] = bbands['Real Middle Band']
        self.data['Lower Band'] = bbands['Real Lower Band']

        macd = self.get_one_indicator('macdext')
        self.data['MACD'] = macd['MACD']
        self.data['MACD Signal'] = macd['MACD_Signal']

        if self.log == 2 or self.log == 3:
            print('\nData with indexes from indexes():')
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            print(self.data)
            pd.reset_option('display.max_rows')
            pd.reset_option('display.max_columns')

        # self.get_one_indicator('stochf')






    def data_maker(self):
        self.yf_downloader()

        if self.getnews == 0:
            self.set_datetime_index_for_data()
            self.data.index = self.data.index.strftime('%Y-%m-%d %H')

            if self.getindexes == 1:
                self.indexes()



        if self.getnews == 1:
            self.better_news_analysis_in_given_interval()
            self.give_as_many_news_scores_and_urls_as_dataline()
            self.data['News scores'] = self.reducated_news_scores
            self.data['News URLs'] = self.reducated_news_urls
            median_analyzing_time = statistics.median(self.analyzing_times)

            if self.getindexes == 1:
                self.indexes()



        if self.log <= 3:
            print('\n\n data:  from data_maker()')
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            print(self.data)
            pd.reset_option('display.max_rows')
            pd.reset_option('display.max_columns')
            if self.getnews == 1:
                print(f'\n\n Average (median) time for analyzing 1 news: {median_analyzing_time} \n\n')











# Example usage
# data_maker = DataMaker('AAPL', '2024-04-10', '2024-04-12', '1h', 'OpenAI', 0, 1,2)
# data_maker.data_maker()





