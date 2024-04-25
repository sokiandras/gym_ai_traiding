import praw
import datetime
import time
import requests
from psaw import PushshiftAPI
import pandas as pd


class Reddit_Scraper():
    def __init__(self, symbol, start_date, end_date, log):
        self.start_date = start_date
        self.end_date = end_date
        self.symbol = symbol
        self.log = log
        self.all_posts_from_topic_subreddit = None
        self.all_posts_from_financial_subreddit = None

        with open('Reddit_API_keys.txt', 'r') as api_keys_file:
            keys = api_keys_file.read().splitlines()

        self.reddit = praw.Reddit(
            client_id = keys[0],
            client_secret = keys[1],
            user_agent = keys[2],
            #username = keys[3],
            #password = keys[4]
        )

        self.reddit.read_only = True  #hogy ne csináljak hülyeséget; ha fel kell oldani, jelszót és felhasználónevet is meg kell adni az init-ben




    def topic_subreddit_decider(self):
        for subreddit in self.reddit.subreddits.search_by_name("apple"):
            print(subreddit.display_name)




    def get_posts_from_topic_subreddit(self):
        start_date_unix = datetime.datetime.strptime(self.start_date, '%Y-%m-%d').timestamp()
        end_date_unix = datetime.datetime.strptime(self.end_date, '%Y-%m-%d').timestamp()
        post_collection = {"Title": [], "Post Text": [], "ID": [], "Score": [], "Upvote Ratio": [],"Total Comments": [], "Created On": [], "Post URL": [], "Original Content": []}

        # for submission in self.reddit.subreddit("apple").top(limit=None, time_filter="all"):

        for submission in self.reddit.subreddit("apple").new(limit=None):
            if self.log == 2 or self.log == 3:
                created_date_normal = datetime.datetime.fromtimestamp(submission.created_utc)
                print(f'created at: {created_date_normal}')
                print(f'Subreddit: {submission.subreddit}')
                print(f'Title: {submission.title}')
                print(f'Upvote ratio: {submission.upvote_ratio}')
                print(f'{submission.selftext}\n\n')

            if submission.created_utc > start_date_unix and submission.created_utc < end_date_unix:
                post_collection["Title"].append(submission.title)
                post_collection["Post Text"].append(submission.selftext)
                post_collection["ID"].append(submission.id)
                post_collection["Score"].append(submission.score)
                post_collection["Upvote Ratio"].append(submission.upvote_ratio)
                post_collection["Total Comments"].append(submission.num_comments)
                post_collection["Created On"].append(submission.created_utc)
                post_collection["Post URL"].append(submission.url)
                post_collection["Original Content"].append(submission.is_original_content)

        all_posts = pd.DataFrame(post_collection)


        all_dates = all_posts['Created On'].map(datetime.datetime.fromtimestamp)
        all_posts = all_posts.assign(Created_On_Normal=all_dates)

        if self.log == 2 or self.log == 3:
            pd.set_option('display.max_rows', None)
            print(all_posts['Created_On_Normal'])
            print('\n\n')
            print(all_posts['Title'])
            pd.reset_option('display.max_rows')

        self.all_posts_from_topic_subreddit = all_posts


    def get_posts_from_financial_subreddits(self):
        start_date_unix = datetime.datetime.strptime(self.start_date, '%Y-%m-%d').timestamp()
        end_date_unix = datetime.datetime.strptime(self.end_date, '%Y-%m-%d').timestamp()
        post_collection = {"Title": [], "Post Text": [], "ID": [], "Score": [], "Upvote Ratio": [], "Total Comments": [], "Created On": [], "Post URL": [], "Original Content": []}

        for submission in self.reddit.subreddit("stocks+StockMarket+wallstreetbets+investing").search(query="apple", sort="new", time_filter="all"):
            if self.log == 2 or self.log == 3:
                created_date_normal = datetime.datetime.fromtimestamp(submission.created_utc)
                print(f'created at: {created_date_normal}')
                print(f'Subreddit: {submission.subreddit}')
                print(f'Title: {submission.title}')
                print(f'Upvote ratio: {submission.upvote_ratio}')
                print(f'{submission.selftext}\n\n')

                submission.comments.replace_more(limit=None)
                for first_level_comment in submission.comments:
                    print(f'level1: {first_level_comment.body}')
                    print('\n')
                    for second_level_comment in first_level_comment.replies:
                        print(f'level2: {second_level_comment.body}')
                        print('\n')


            if submission.created_utc > start_date_unix and submission.created_utc < end_date_unix:
                post_collection["Title"].append(submission.title)
                post_collection["Post Text"].append(submission.selftext)
                post_collection["ID"].append(submission.id)
                post_collection["Score"].append(submission.score)
                post_collection["Upvote Ratio"].append(submission.upvote_ratio)
                post_collection["Total Comments"].append(submission.num_comments)
                post_collection["Created On"].append(submission.created_utc)
                post_collection["Post URL"].append(submission.url)
                post_collection["Original Content"].append(submission.is_original_content)

        all_posts = pd.DataFrame(post_collection)

        all_dates = all_posts['Created On'].map(datetime.datetime.fromtimestamp)
        all_posts = all_posts.assign(Created_On_Normal=all_dates)

        if self.log == 2 or self.log == 3:
            pd.set_option('display.max_rows', None)
            print(all_posts['Created_On_Normal'])
            print('\n\n')
            print(all_posts['Title'])
            pd.reset_option('display.max_rows')

        self.all_posts_from_financial_subreddit = all_posts







scraper = Reddit_Scraper('AAPL', '2024-04-15', '2024-04-20', 2)
scraper.topic_subreddit_decider()
#scraper.get_posts_from_topic_subreddit()
#scraper.get_posts_from_financial_subreddits()