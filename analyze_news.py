from chatgpt import AI
from news import News
import statistics


class Analyze_news():
    def __init__(self, symbol, date, hour, log):
        self.symbol = symbol
        self.date = date
        self.hour = hour
        self.log = log
        self.scores = []



    def analyze(self):
        ai = AI("OpenAI")
        news = News('NewsAPI', self.log)
        there_are_articles_and_full_texts = news.search_and_get_full_content(self.symbol, self.date, self.hour)
        if there_are_articles_and_full_texts == 1:
            for i, (article_title, article_content, article_url) in enumerate(zip(news.filtered_article_titles, news.filtered_article_contents, news.filtered_article_urls)):
                sentiment_score = ai.analyze_sentiment_chat(article_content)
                try:
                    sentiment_score_float = float(sentiment_score)
                except ValueError:
                    sentiment_score_float = 5
                if self.log == 2 or self.log == 3:
                    print(f"\n\n\nSentiment score for Article {i+1}: title: {article_title}: {sentiment_score} (message from analyze())")
                    print(f"\nArticle URL: {article_url} (message from analyze())")
                self.scores.append(sentiment_score_float)

            if self.log == 2 or self.log == 3:
                print(f"\nScore list from hour {self.hour}: {self.scores} (message from analyze())")

            average_score = statistics.mean(self.scores)
            return average_score

        else:
            if self.log == 2 or self.log == 3:
                print(f"\n\n\nThere were no analyzable news in hour {self.hour} (message from analyze())")
            return -1









#test = Analyze_news('AAPL', '2023-11-14', hour=13, log=1)
#test = Analyze_news('AAPL', '2023-11-14', hour=13, log=1)
#average_score = test.analyze()
#print("\nAverage score: ", average_score)