import openai.error
import time
from chatgpt import AI
from news import News
import statistics


class Analyze_news():
    def __init__(self, symbol, date, ai_type, log): #a date után be kell rakni a hour-t hogy a régi módszerrel működjön
        self.symbol = symbol
        self.date = date
        #self.hour = hour
        self.log = log
        self.scores = []
        self.ai_type = ai_type

        self.news = None


    def get_news_for_a_day(self):
        self.news = News('NewsAPI', self.log)
        self.news.search_news_for_a_day(self.symbol, self.date)


    def analyze_for_an_hour(self, hour):
        ai = AI(self.ai_type)
        #ai = AI("OpenAI")
        # news = News('NewsAPI', self.log)
        # news.search_news_for_a_day(self.symbol, self.date)
        self.scores.clear()
        there_are_articles_in_the_hour = self.news.filter_news_for_hour(hour)
        if there_are_articles_in_the_hour:
            there_are_full_texts_in_the_hour = self.news.get_full_texts_from_an_hour()
            if there_are_full_texts_in_the_hour:
                max_retries=5
                for i in range(max_retries):
                    try:

                        for i, (article_title, article_content, article_url) in enumerate(zip(self.news.articles_in_an_hour_titles, self.news.articles_in_an_hour_contents, self.news.articles_in_an_hour_urls)):
                            sentiment_score = ai.analyze_sentiment_chat(article_content)
                            try:
                                sentiment_score_float = float(sentiment_score)
                            except ValueError:
                                sentiment_score_float = 5
                            if self.log == 2 or self.log == 3:
                                print(f"\n\n\nSentiment score for Article {i + 1}: title: {article_title}: {sentiment_score} (message from analyze_for_an_hour())")
                                print(f"\nArticle URL: {article_url} (message from analyze_for_an_hour())")
                            self.scores.append(sentiment_score_float)
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
                return average_score

            else:
                if self.log == 2 or self.log == 3:
                    print(f"\n\n\nThere were no analyzable news in hour {hour} (message from analyze_for_an_hour())")
                return -1



# test = Analyze_news('AAPL', '2024-03-06', log=3)
# # average_score = test.analyze()
# # print("\nAverage score: ", average_score)
# test.get_news_for_a_day()
# average_score2 = test.analyze_for_an_hour(13)
# print("\nAverage score 2: ", average_score2)