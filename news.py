from newsapi import NewsApiClient
from datetime import datetime
import os
import requests
from newsplease import NewsPlease
from analyzed_news_class import One_News



class News():
    def __init__(self, api_type, log):
        self.api_type = api_type
        self.symbol = None
        self.date = None
        self.hour = None
        self.log = log

        if self.api_type == "NewsAPI":
            self.api_key = open("NEWS_API_KEY.txt","r").read()

        elif self.api_type == 'NewsData.io':
            self.api_key = open("NewsData_API_key.txt","r").read()

        else:
            print("Incorrect api type")

        self.session = requests.session()

        self.filtered_articles =[]
        self.filtered_article_urls = None
        self.filtered_article_titles = []
        self.filtered_article_contents = []

        self.all_news_in_a_day = None
        self.all_articles_in_a_day =[]
        self.articles_in_an_hour =[]
        self.articles_in_an_hour_urls = []
        self.articles_in_an_hour_titles =[]
        self.articles_in_an_hour_contents = []





    def search_news_for_a_day(self, symbol, date):
        self.symbol = symbol
        self.date = date

        if (self.api_type == "NewsAPI"):
            base_url = 'https://newsapi.org/v2/everything?'

        query = f'q={self.symbol}'
        from_date = f'from={self.date}'
        end_date = f'to={self.date}'
        sort_by = 'sortBy=popularity'
        api_key = f'apiKey={self.api_key}'

        if (self.api_type == "NewsAPI"):
            url = f'{base_url}{query}&{from_date}&{end_date}&{sort_by}&{api_key}'

        response = self.session.get(url)
        if response.status_code != 200:
            print(f"\nError with NewsAPI request: {response.json()['message']}")
            return -1

        self.all_news_in_a_day = response.json()
        if self.log == 3:
            print("All news from the day: (given by NewsAPI) (message from search_news_for_a_day())\n")
            print(self.all_news_in_a_day)

        if self.all_news_in_a_day['status'] == 'ok':
            self.all_articles_in_a_day = self.all_news_in_a_day['articles']

        if self.all_news_in_a_day['status'] == 'error':
            if self.log <= 3:
                print("\nThere was some problem with NewsAPI news search (message from search_news_for_a_day())\n")
            return -1



    def filter_news_for_hour(self, hour):
        self.articles_in_an_hour.clear()
        self.articles_in_an_hour_urls.clear()
        self.articles_in_an_hour_titles.clear()
        self.articles_in_an_hour_contents.clear()

        self.articles_in_an_hour = [article for article in self.all_news_in_a_day['articles'] if datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').hour == hour]

        for article in self.articles_in_an_hour:
            self.articles_in_an_hour_urls.append(article.get('url'))

        if self.log == 3:
            print(f"\n\nFiltered article URLs from hour {hour} (message from filter_news_for_hour()\n")
            print(self.articles_in_an_hour_urls)

        if not self.articles_in_an_hour_titles:
            self.articles_in_an_hour_titles = []
        if not self.articles_in_an_hour_contents:
            self.articles_in_an_hour_contents = []
        if not self.articles_in_an_hour_urls:
            self.articles_in_an_hour_urls = []

        if not self.articles_in_an_hour:
            if self.log  == 3:
                print("\nThere were no news in the given hour (message from search_news())")
            return -1
        else:
            return 1






    def get_full_texts_from_an_hour(self):
        if self.log == 3:
            print("\n\n\nURLSs, titles and full contents of articles (from news-please) (message from get_full_text_from_an_hour()):\n")

        urls_without_full_text = []
        for current_article_url in self.articles_in_an_hour_urls:
            try:
                article = NewsPlease.from_url(current_article_url)
                self.articles_in_an_hour_titles.append(article.title)
                self.articles_in_an_hour_contents.append(article.maintext)
                if self.log == 3:
                    print("\nCurrent article URL: ", current_article_url)
                    print('\nArticle title: ', article.title)
                    print("\nArticle maintext: ", article.maintext)

            except Exception as e:
                if self.log == 3:
                    print(f"\nSkipping invalid or missing 'maintext' attribute for URL: {current_article_url}, (message from get_full_texts_from_an_hour())")
                    print(f"Error processing URL {current_article_url}: {e}")
                urls_without_full_text.append(current_article_url)
                continue  # Move to the next URL in case of an error

        for url in urls_without_full_text:
            self.articles_in_an_hour_urls.remove(url)

        if not self.filtered_article_titles:
            self.filtered_article_titles = []
        if not self.filtered_article_contents:
            self.filtered_article_contents = []
        if not self.filtered_article_urls:
            self.filtered_article_urls = []

        if not self.articles_in_an_hour_contents:
            if(self.log == 3):
                print("\nThere were no content in the article (message from get_full_texts_from_an_hour()")
            return 0

        return 1



    def get_full_texts_from_an_hour_with_one_news_class(self):  #próbálkozás, nincs használatban
        if self.log == 3:
            print("\n\n\nURLSs, titles and full contents of articles (from news-please) (message from get_full_text_from_an_hour()):\n")

        urls_without_full_text = []
        for current_article_url in self.articles_in_an_hour_urls:
            try:
                article = NewsPlease.from_url(current_article_url)
                title = article.title
                content = article.maintext

                one_news = One_News(self.hour, )

                self.articles_in_an_hour_titles.append(article.title)
                self.articles_in_an_hour_contents.append(article.maintext)
                if self.log == 3:
                    print("\nCurrent article URL: ", current_article_url)
                    print('\nArticle title: ', article.title)
                    print("\nArticle maintext: ", article.maintext)

            except Exception as e:
                if self.log == 3:
                    print(f"\nSkipping invalid or missing 'maintext' attribute for URL: {current_article_url}, (message from get_full_texts_from_an_hour())")
                    print(f"Error processing URL {current_article_url}: {e}")
                urls_without_full_text.append(current_article_url)
                continue  # Move to the next URL in case of an error

        for url in urls_without_full_text:
            self.articles_in_an_hour_urls.remove(url)

        if not self.filtered_article_titles:
            self.filtered_article_titles = []
        if not self.filtered_article_contents:
            self.filtered_article_contents = []
        if not self.filtered_article_urls:
            self.filtered_article_urls = []

        if not self.articles_in_an_hour_contents:
            if(self.log == 3):
                print("\nThere were no content in the article (message from get_full_texts_from_an_hour()")
            return 0

        return 1





# news = News('NewsAPI', 1)
# news.search_news('AAPL', '2023-11-14', 13)
#news.get_full_text()
#news.save_news()

