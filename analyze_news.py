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
                sentiment_score_float = float(sentiment_score)
                if (self.log):
                    print(f"\n\nSentiment score for Article {i+1}: title: {article_title}: {sentiment_score}")
                    print(f"\nArticle URL: {article_url}")
                self.scores.append(sentiment_score_float)

            if self.log:
                print("\nscore list: ", self.scores)

            average_score = statistics.mean(self.scores)
            return average_score

        else:
            if self.log:
                print("\nThere were no analyzable news (message from analyze())")
            return -1









#test = Analyze_news('AAPL', '2023-11-14', hour=13, log=1)
test = Analyze_news('AAPL', '2023-11-14', hour=13, log=1)
average_score = test.analyze()
print("\nAverage score: ", average_score)