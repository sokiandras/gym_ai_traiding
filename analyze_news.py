import openai.error
import time
from chatgpt import AI
from news import News
import statistics
import time


class Analyze_news():
    def __init__(self, symbol, date, ai_type, analyzing_times, log): #a date után be kell rakni a hour-t hogy a régi módszerrel működjön
        self.symbol = symbol
        self.date = date
        #self.hour = hour
        self.log = log
        self.scores = []
        self.ai_type = ai_type
        self.analyzing_times = analyzing_times
        self.news = None

        # self.total_articles_in_the_hour = 0
        # self.articles_with_maintext_in_the_hour = 0
        self.articles_without_maintext_in_the_hour = 0
        self.number_of_news_in_a_day = 0
        self.articles_cant_be_analyzed = 0

    def get_news_for_a_day(self):
        self.news = News('NewsAPI', self.log)
        self.news.search_news_for_a_day(self.symbol, self.date)
        self.number_of_news_in_a_day = self.news.number_of_news_in_a_day


    def analyze_for_an_hour(self, hour):
        ai = AI(self.ai_type)
        self.scores.clear()

        # self.news.total_articles = 0
        # self.news.articles_with_maintext = 0

        there_are_articles_in_the_hour = self.news.filter_news_for_hour(hour)
        if there_are_articles_in_the_hour:
            there_are_full_texts_in_the_hour = self.news.get_full_texts_from_an_hour()
            #self.total_articles_in_the_hour = self.news.number_of_total_articles
            #self.articles_with_maintext_in_the_hour = self.news.number_of_articles_with_full_texts
            self.articles_without_maintext_in_the_hour = self.news.number_of_articles_without_texts

            if there_are_full_texts_in_the_hour:
                max_retries=6

                for i in range(max_retries):
                    try:
                        hourly_urls = []
                        for i, (article_title, article_content, article_url) in enumerate(zip(self.news.articles_in_an_hour_titles, self.news.articles_in_an_hour_contents, self.news.articles_in_an_hour_urls)):
                            start_time = time.time()
                            sentiment_score = ai.analyze_sentiment_chat(article_content)
                            end_time = time.time()
                            time_took = round(end_time - start_time, 3)
                            self.analyzing_times.append(time_took)
                            try:
                                sentiment_score_float = float(sentiment_score)
                            except ValueError:
                                self.articles_cant_be_analyzed += 1
                                sentiment_score_float = 5
                            if self.log == 2 or self.log == 3:
                                print(f"\n\n\nSentiment score for Article {i + 1}: title: {article_title}, score: {sentiment_score}, time: {time_took}s (analyze_for_an_hour())")
                                print(f"\nArticle URL: {article_url} (message from analyze_for_an_hour())")
                            self.scores.append(sentiment_score_float)

                            hourly_urls.append(article_url)

                        break # If no exception was raised, break the loop
                    except openai.error.OpenAIError as e:
                        print("\n\nAn error occured from OpenAI, try again in 5s (message from analyze_for_an_hour()\n")
                        if i<max_retries-1:
                            time.sleep(5)
                            continue
                        else:
                            raise

                if self.log == 2 or self.log == 3:
                    print(f"\nScore list from hour {hour}: {self.scores} (message from analyze_for_an_hour())")

                average_score = statistics.mean(self.scores)
                # self.total_articles_in_the_hour = self.news.total_articles
                # self.articles_with_maintext_in_the_hour = self.news.articles_with_maintext
                return average_score, hourly_urls

            else:
                if self.log == 2 or self.log == 3:
                    print(f"\n\n\nThere were no analyzable news in hour {hour} (message from analyze_for_an_hour())")
                return -1, []


        else:
            if self.log == 2 or self.log == 3:
                print(f"\n\n\nThere were no analyzable news in hour {hour} (message from analyze_for_an_hour())")
            return -1,






# analyzing_times = []
# test = Analyze_news('AAPL', '2024-10-23', "OpenAI", analyzing_times, log=3)
# test.get_news_for_a_day()
# average_score = test.analyze_for_an_hour(14)
# print("\nAverage score: ", average_score)
# print("\nAnalyzing times: ", analyzing_times)