import praw
import datetime
import time
import pandas as pd
from chatgpt import AI
from comment_analyzer import Comment_Analyzer



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
        chosen_subreddit = self.topic_subreddit_decider('choose subreddit')
        start_date_unix = datetime.datetime.strptime(self.start_date, '%Y-%m-%d').timestamp()
        end_date_unix = datetime.datetime.strptime(self.end_date, '%Y-%m-%d').timestamp()
        post_collection = {"Title": [], "Post Text": [], "Upvote Ratio": [],"Number of comments": [], "Created at": [], "Post URL": [], "Sentiment score": []}

        # for submission in self.reddit.subreddit("apple").top(limit=None, time_filter="all"):

        for submission in self.reddit.subreddit(chosen_subreddit).new(limit=None):
            if start_date_unix < submission.created_utc < end_date_unix:  # csak akkor analizálunk, ha benne van az időben
                try:
                    start_time = time.time()
                    analyzer = Comment_Analyzer(self.log)
                    score = analyzer.one_message_analyzer(submission.title + " " + submission.selftext)
                    end_time = time.time()
                    time_taken = end_time - start_time
                except RuntimeError:
                    continue
            else:
                score = None
                time_taken = None

            if self.log == 2 or self.log == 3:
                created_date_normal = datetime.datetime.fromtimestamp(submission.created_utc)
                print(f'created at: {created_date_normal}')
                print(f'Subreddit: {submission.subreddit}')
                print(f'Title: {submission.title}')
                print(f'Upvote ratio: {submission.upvote_ratio}')
                print(f'Sentiment score: {score}')
                print(f'Analyzing time: {time_taken} s')
                print(f'{submission.selftext}\n\n\n')

                if comments == 1:
                    submission.comments.replace_more(limit=None)
                    for first_level_comment in submission.comments:
                        print(f'level1: {first_level_comment.body}')
                        print('\n')
                        for second_level_comment in first_level_comment.replies:
                            print(f'level2: {second_level_comment.body}')
                            print('\n')

            if start_date_unix < submission.created_utc < end_date_unix:
                post_collection["Title"].append(submission.title)
                post_collection["Post Text"].append(submission.selftext)
                post_collection["Upvote Ratio"].append(submission.upvote_ratio)
                post_collection["Number of comments"].append(submission.num_comments)
                post_collection["Created at"].append(submission.created_utc)
                post_collection["Post URL"].append(submission.url)
                post_collection['Sentiment score'].append(score)

        all_posts = pd.DataFrame(post_collection)


        all_dates = all_posts['Created at'].map(datetime.datetime.fromtimestamp)
        all_posts = all_posts.assign(Created_at_Normal=all_dates)

        if self.log == 2 or self.log == 3:
            # pd.set_option('display.max_rows', None)
            # print(all_posts['Created_On_Normal'])
            # print('\n\n')
            # print(all_posts['Title'])
            # pd.reset_option('display.max_rows')

            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            print(all_posts)
            pd.reset_option('display.max_rows')
            pd.reset_option('display.max_columns')

        self.all_posts_from_topic_subreddit = all_posts



    def get_posts_from_financial_subreddits(self, comments):
        start_date_unix = datetime.datetime.strptime(self.start_date, '%Y-%m-%d').timestamp()
        end_date_unix = datetime.datetime.strptime(self.end_date, '%Y-%m-%d').timestamp()
        choosen_subreddit = self.topic_subreddit_decider('finance subreddit')
        post_collection = {"Title": [], "Post Text": [], "Upvote Ratio": [],"Number of comments": [], "Created at": [], "Post URL": [], "Sentiment score": []}

        for submission in self.reddit.subreddit("stocks+StockMarket+wallstreetbets+investing").search(query=choosen_subreddit, sort="new", time_filter="all"):
            if start_date_unix < submission.created_utc < end_date_unix:  # csak akkor analizálunk, ha benne van az időben
                try:
                    start_time = time.time()
                    analyzer = Comment_Analyzer(self.log)
                    score = analyzer.one_message_analyzer(submission.title + " " + submission.selftext)
                    end_time = time.time()
                    time_taken = end_time - start_time
                except RuntimeError:
                    continue
            else:
                score = None
                time_taken = None

            if self.log == 2 or self.log == 3:
                created_date_normal = datetime.datetime.fromtimestamp(submission.created_utc)
                print(f'created at: {created_date_normal}')
                print(f'Subreddit: {submission.subreddit}')
                print(f'Title: {submission.title}')
                print(f'Upvote ratio: {submission.upvote_ratio}')
                print(f'Sentiment score: {score}')
                print(f'Analyzing time: {time_taken} s')
                print(f'{submission.selftext}\n\n\n')

                if comments == 1:
                    submission.comments.replace_more(limit=None)
                    for first_level_comment in submission.comments:
                        print(f'level1: {first_level_comment.body}')
                        print('\n')
                        for second_level_comment in first_level_comment.replies:
                            print(f'level2: {second_level_comment.body}')
                            print('\n')


            if start_date_unix < submission.created_utc < end_date_unix:
                post_collection["Title"].append(submission.title)
                post_collection["Post Text"].append(submission.selftext)
                post_collection["Upvote Ratio"].append(submission.upvote_ratio)
                post_collection["Number of comments"].append(submission.num_comments)
                post_collection["Created at"].append(submission.created_utc)
                post_collection["Post URL"].append(submission.url)
                post_collection["Sentiment score"].append(score)

        all_posts = pd.DataFrame(post_collection)

        all_dates = all_posts['Created at'].map(datetime.datetime.fromtimestamp)
        all_posts = all_posts.assign(Created_at_Normal=all_dates)

        if self.log == 2 or self.log == 3:
            # pd.set_option('display.max_rows', None)
            # print(all_posts['Created_On_Normal'])
            # print('\n\n')
            # print(all_posts['Title'])
            # pd.reset_option('display.max_rows')

            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            print(all_posts)
            pd.reset_option('display.max_rows')
            pd.reset_option('display.max_columns')

        self.all_posts_from_financial_subreddit = all_posts





    def merge_collections_from_subreddits(self):
        if not self.all_posts_from_topic_subreddit.empty and not self.all_posts_from_financial_subreddit.empty:
            self.merged_posts = pd.concat([self.all_posts_from_topic_subreddit, self.all_posts_from_financial_subreddit])
            self.merged_posts = self.merged_posts.sort_values(by="Created at")
            if self.log == 2 or self.log == 3:
                pd.set_option('display.max_rows', None)
                pd.set_option('display.max_columns', None)
                print(self.merged_posts)
                pd.reset_option('display.max_rows')
                pd.reset_option('display.max_columns')


    def data_into_hourly_averages(self):  # NEM JÓ TELJESEN !!!!!!
        self.hourly_sentiment = self.merged_posts
        self.hourly_sentiment['Created at'] = pd.to_datetime(self.hourly_sentiment['Created at'], unit='s')
        self.hourly_sentiment.set_index('Created at', inplace=True)
        self.hourly_sentiment = self.merged_posts['Sentiment score'].resample('H').mean()
        if self.log == 2 or self.log == 3:
            print("\n\nSentiment values hourly: ")
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            print(self.hourly_sentiment)
            pd.reset_option('display.max_rows')
            pd.reset_option('display.max_columns')




    def collect_from_reddit(self):
        self.get_posts_from_topic_subreddit(0)
        self.get_posts_from_financial_subreddits(0)
        self.merge_collections_from_subreddits()
        self.data_into_hourly_averages()










scraper = Reddit_Scraper('AAPL', '2024-05-06', '2024-05-08', 3)
scraper.collect_from_reddit()
