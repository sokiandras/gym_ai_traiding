import praw
import datetime
import time
import requests
from psaw import PushshiftAPI
import pandas as pd
from chatgpt import AI


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




    def topic_subreddit_decider(self, usage):
        ai = AI("OpenAI")
        company_name, _, _ = ai.chat(
            f'What is the company name associated with the ticker "{self.symbol}"? Please provide the company name in lowercase letters only, without any additional text such as "Inc." or similar variations.')
        print(f'Possible company name: {company_name}')

        if usage == 'finance subreddit':
            return company_name

        if usage == 'choose subreddit':
            print('\nSubreddits with company name: ')
            subreddit_list = list(self.reddit.subreddits.search_by_name(company_name))
            for i, subreddit in enumerate(subreddit_list):
                print(f'{i + 1}. {subreddit.display_name}')

            choice = int(input("Enter the number of the subreddit you want to choose: ")) - 1
            chosen_subreddit = subreddit_list[choice].display_name
            print(f'You have chosen: r/{chosen_subreddit} subreddit\n\n')
            return chosen_subreddit




    def get_posts_from_topic_subreddit(self, comments):
        choosen_subreddit = self.topic_subreddit_decider('choose subreddit')
        start_date_unix = datetime.datetime.strptime(self.start_date, '%Y-%m-%d').timestamp()
        end_date_unix = datetime.datetime.strptime(self.end_date, '%Y-%m-%d').timestamp()
        post_collection = {"Title": [], "Post Text": [], "ID": [], "Score": [], "Upvote Ratio": [],"Total Comments": [], "Created On": [], "Post URL": [], "Original Content": []}

        # for submission in self.reddit.subreddit("apple").top(limit=None, time_filter="all"):

        for submission in self.reddit.subreddit(choosen_subreddit).new(limit=None):
            if self.log == 2 or self.log == 3:
                created_date_normal = datetime.datetime.fromtimestamp(submission.created_utc)
                print(f'created at: {created_date_normal}')
                print(f'Subreddit: {submission.subreddit}')
                print(f'Title: {submission.title}')
                print(f'Upvote ratio: {submission.upvote_ratio}')
                print(f'{submission.selftext}\n\n')

                if comments == 1:
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

        self.all_posts_from_topic_subreddit = all_posts



    def get_posts_from_financial_subreddits(self, comments):
        start_date_unix = datetime.datetime.strptime(self.start_date, '%Y-%m-%d').timestamp()
        end_date_unix = datetime.datetime.strptime(self.end_date, '%Y-%m-%d').timestamp()
        choosen_subreddit = self.topic_subreddit_decider('finance subreddit')
        post_collection = {"Title": [], "Post Text": [], "ID": [], "Score": [], "Upvote Ratio": [], "Total Comments": [], "Created On": [], "Post URL": [], "Original Content": []}

        for submission in self.reddit.subreddit("stocks+StockMarket+wallstreetbets+investing").search(query=choosen_subreddit, sort="new", time_filter="all"):
            if self.log == 2 or self.log == 3:
                created_date_normal = datetime.datetime.fromtimestamp(submission.created_utc)
                print(f'created at: {created_date_normal}')
                print(f'Subreddit: {submission.subreddit}')
                print(f'Title: {submission.title}')
                print(f'Upvote ratio: {submission.upvote_ratio}')
                print(f'{submission.selftext}\n\n')

                if comments == 1:
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







scraper = Reddit_Scraper('NVDA', '2024-04-15', '2024-04-20', 2)
scraper.get_posts_from_topic_subreddit(0)
scraper.get_posts_from_financial_subreddits(0)