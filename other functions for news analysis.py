from stockmarketenv import StockMarketEnv
from newsapi import NewsApiClient
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
import newspaper
from lxml import html
from readability import Document
from newsplease import NewsPlease


class NewsAnalysis():
    def __init__(self, api_type):
        self.api_type = api_type
        self.symbol = None
        self.date = None
        self.hour = None

        if self.api_type == "NewsAPI":
            self.api_key = open("NEWS_API_KEY.txt", "r").read()

        elif self.api_type == 'NewsData.io':
            self.api_key = open("NewsData_API_key.txt", "r").read()

        else:
            print("Incorrect api type")

        self.session = requests.session()

        self.filtered_articles = []
        self.filtered_article_urls = None
        self.filtered_article_titles = []
        self.filtered_article_contents = []

    def analyze_news(self, symbol, date, hour):
        self.symbol = symbol
        self.date = date
        self.hour = hour

        if (self.api_type == "NewsAPI"):
            base_url = 'https://newsapi.org/v2/everything?'
        elif (self.api_type == "NewsData.io"):
            base_url = 'https://newsdata.io/api/1/news?'

        query = f'q={self.symbol}'
        from_date = f'from={self.date}'
        end_date = f'to={self.date}'
        sort_by = 'sortBy=popularity'
        api_key = f'apiKey={self.api_key}'

        if (self.api_type == "NewsAPI"):
            url = f'{base_url}{query}&{from_date}&{end_date}&{sort_by}&{api_key}'
        elif (self.api_type == "NewsData.io"):
            url = f'{base_url}{api_key}&{query}'

        response = self.session.get(url)
        news = response.json()
        print("All news from the day:\n")
        print(news)

        if news['status'] == 'ok':
            target_hour = self.hour
            self.filtered_articles = [article for article in news['articles'] if
                                      datetime.strptime(article['publishedAt'],
                                                        '%Y-%m-%dT%H:%M:%SZ').hour == target_hour]

            self.filtered_article_urls = []
            for article in self.filtered_articles:
                self.filtered_article_urls.append(article.get('url'))

        if not self.filtered_articles:
            print("There were no news in the given hour")
            return 0

        else:
            print('\nFiltered URLs from the given hour: \n')
            print(self.filtered_article_urls)
            print('\nFiltered articles: \n')
            print(self.filtered_articles)
            return 1

    def get_full_text(self):
        for current_article_url in self.filtered_article_urls:
            try:
                article = NewsPlease.from_url(current_article_url)
                self.filtered_article_titles.append(article.title)
                self.filtered_article_contents.append(article.maintext)
                print("\nCurrent article URL: ", current_article_url)
                print('\nArticle title: ', article.title)
                print("\nArticle maintext: ", article.maintext)

            except Exception as e:
                print(f"Skipping invalid or missing 'maintext' attribute for URL: {current_article_url}")
                print(f"Error processing URL {current_article_url}: {e}")
                continue  # Move to the next URL in case of an error

    def readability(self):
        for current_article in self.filtered_articles:
            print("Current article: ", current_article['title'])
            article_url = current_article.get('url')
            article_response = self.session.get(article_url)

            if article_response.status_code == 200:
                article_html = article_response.content
                readable_article = Document(article_html)
                article_content = readable_article.summary()

                # Using BeautifulSoup to extract text from HTML
                soup = BeautifulSoup(article_content, 'html.parser')
                article_text = soup.get_text(separator='\n')

                print("\nArticle text: \n")
                print(article_text.strip())
            else:
                print(f"\nFailed to fetch article content for {current_article['title']}")

    def fetch_articles(self):
        self.article_contents = {}
        print("Fetching articles")

        for article_url in self.filtered_article_urls:
            print(f'Current article URL: {article_url}')
            response = self.session.get(article_url)

            if response.status_code == 200:
                print('\nresponse: 200')
                soup = BeautifulSoup(response.content, 'html.parser')
                current_article = soup.select_one('article')

                if current_article:
                    current_article_content = current_article.get_text()
                    print('Current article content: \n')
                    print(current_article_content)
                    self.article_contents[article_url] = current_article_content
                else:
                    print(f"Could not find the article element in {article_url}")

            else:
                print('respone !=200')
                print(f"Failed to fetch content from {article_url}")

        print('Article contents: \n')
        print(self.article_contents)

    def whole_articles(self):
        test_url = 'https://www.investors.com/market-trend/stock-market-today/dow-jones-futures-oil-prices-spike-on-us-sanctions-jpmorgan-unitedhealth-earnings-beat/'
        article = newspaper.Article(test_url)
        article.download()
        article.parse()
        print("Ez a whole article\n")
        print(article.text)

    def save_news(self):

        if not self.filtered_articles:
            print("There was no news in that hour, there are nothing to save")
            return 0

        base_directory = r'D:\Egyetem\Önlab\onlab2\news'
        output_directory = os.path.join(base_directory, f'{self.symbol}_news_{self.date}')
        os.makedirs(output_directory, exist_ok=True)

        for i, article in enumerate(self.filtered_articles):
            content = article.get('content', '')
            if content:
                filename = os.path.join(output_directory, f'{self.symbol} {self.date} {self.hour} {i + 1}.txt')
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(content)
                print(f"Article {i + 1} saved to {filename}")


news = NewsAnalysis('NewsAPI')
news.analyze_news('AAPL', '2023-11-14', 13)
news.get_full_text()

# news.fetch_articles()
# news.whole_articles()
# news.readability()
# news.save_news()