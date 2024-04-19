import yfinance as yf
import pandas as pd
import datetime
import openai
import statistics
from analyze_news import Analyze_news
from yahoo_fin.stock_info import get_quote_table, get_data


class DataMaker():
    def __init__(self, symbol, start_date, end_date, data_interval, ai_type, getnews, log):
        self.stock_symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.data_interval = data_interval
        self.ai_type = ai_type
        self.getnews = getnews
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

        print("Yahoo finance data: \n")
        print(self.data.head())




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

        if self.log <= 3:
            print('\ndata:\n')
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










    def data_maker(self):
        self.yf_downloader()

        if self.getnews == 0:
            self.set_datetime_index_for_data()
            self.data.index = self.data.index.strftime('%Y-%m-%d %H')

        if self.getnews == 1:
            self.better_news_analysis_in_given_interval()
            self.give_as_many_news_scores_and_urls_as_dataline()
            self.data['News scores'] = self.reducated_news_scores
            self.data['News URLs'] = self.reducated_news_urls
            median_analyzing_time = statistics.median(self.analyzing_times)

        if self.log <= 3:
            print('\n\n data: ')
            print(self.data.head(10))
            if self.getnews == 1:
                print(f'\n\n Average (median) time for analyzing 1 news: {median_analyzing_time} \n\n')






# Example usage
# data_maker = DataMaker('AAPL', '2024-04-10', '2024-04-12', '1h', 'OpenAI', 2)
# #data_maker.yf_downloader()
# data_maker.data_maker()






#
# # Your ALPHA VANTAGE API key
# api_key = 'YOUR_API_KEY'
#
# # Initialize TimeSeries and TechIndicators with your API key
# ts = TimeSeries(key=api_key, output_format='pandas')
# ti = TechIndicators(key=api_key, output_format='pandas')
#
# # Get daily stock prices for AAPL
# prices, _ = ts.get_daily(symbol='AAPL', outputsize='full')
# prices = prices['2024-03-15':'2024-03-19']
#
# # Get SMA, EMA, and RSI for AAPL
# sma, _ = ti.get_sma(symbol='AAPL', interval='60min', time_period=20, series_type='close')
# ema, _ = ti.get_ema(symbol='AAPL', interval='60min', time_period=20, series_type='close')
# rsi, _ = ti.get_rsi(symbol='AAPL', interval='60min', time_period=14, series_type='close')
#
# # Trim the date range for the indicators to match the prices DataFrame
# sma = sma['2024-03-15':'2024-03-19']
# ema = ema['2024-03-15':'2024-03-19']
# rsi = rsi['2024-03-15':'2024-03-19']
#
# # Combine all data into a single DataFrame
# combined_df = pd.concat([prices, sma, ema, rsi], axis=1)
# combined_df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA', 'EMA', 'RSI']
#
# # Display the DataFrame
# print(combined_df)
#
# # Optionally, plot the data
# combined_df[['Close', 'SMA', 'EMA']].plot(figsize=(10, 5))
# plt.title('AAPL Prices and Indicators')
# plt.show()