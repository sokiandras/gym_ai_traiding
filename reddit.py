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
        self.start_date_unix = datetime.datetime.strptime(self.start_date, '%Y-%m-%d').timestamp()
        self.end_date_unix = datetime.datetime.strptime(self.end_date, '%Y-%m-%d').timestamp()
        self.symbol = symbol
        self.log = log
        self.temp_collection = None
        self.all_posts_from_topic_subreddit = None
        self.all_posts_from_financial_subreddit = None

        self.score_list = []

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

            #!!!!! itt bypass-oltam a subreddit választást
            choice = int(input("Enter the number of the subreddit you want to choose: ")) - 1
            #choice = 2
            chosen_subreddit = subreddit_list[choice].display_name
            print(f'You have chosen: r/{chosen_subreddit} subreddit\n\n')
            return chosen_subreddit


    def go_through_posts(self, submission, comments):

        if self.start_date_unix < submission.created_utc < self.end_date_unix:  # csak akkor analizálunk, ha benne van az időben

            if self.log == 2 or self.log == 3:  # komment mutató
                if comments == 1:
                    submission.comments.replace_more(limit=None)
                    for first_level_comment in submission.comments:
                        print(f'level1: {first_level_comment.body}')
                        print('\n')
                        for second_level_comment in first_level_comment.replies:
                            print(f'level2: {second_level_comment.body}')
                            print('\n')

            if self.log == 2 or self.log == 3: # képernyőre logoló
                created_date_normal = datetime.datetime.utcfromtimestamp(submission.created_utc)
                print(f'\n\n\nCreated at: {created_date_normal}')
                # print(f'created_utc: {submission.created_utc}')
                print(f'Subreddit: {submission.subreddit}')
                print(f'Title: {submission.title}')
                print(f'Upvote ratio: {submission.upvote_ratio}')
                print(f'Post: {submission.selftext}')

            try:
                start_time = time.time()
                analyzer = Comment_Analyzer(self.log)
                score = analyzer.one_message_analyzer(submission.title + " " + submission.selftext)
                end_time = time.time()
                time_taken = end_time - start_time
                if self.log == 2 or self.log == 3:
                    print(f'sentiment score: {score}')
                    print(f'Analyzing time: {time_taken}')
            except RuntimeError:
                return

            if self.log == 2 or self.log == 3:
                print('----------------------------------------------------------------------------------------')

        else:
            score = None
            time_taken = None
            submission = None


        return submission, score









    def get_posts_from_topic_subreddit(self, comments):
        chosen_subreddit = self.topic_subreddit_decider('choose subreddit')
        post_collection = {"Title": [], "Subreddit": [], "Post Text": [], "Upvote Ratio": [],"Number of comments": [], "Created at": [], "Post URL": [], "Sentiment score": []}

        for submission in self.reddit.subreddit(chosen_subreddit).new(limit=None):
            checked_submission, score = self.go_through_posts(submission, comments)
            if checked_submission is not None and score is not None:
                post_collection["Title"].append(checked_submission.title)
                post_collection['Subreddit'].append(checked_submission.subreddit)
                post_collection["Post Text"].append(checked_submission.selftext)
                post_collection["Upvote Ratio"].append(checked_submission.upvote_ratio)
                post_collection["Number of comments"].append(checked_submission.num_comments)
                post_collection["Created at"].append(checked_submission.created_utc)
                post_collection["Post URL"].append(checked_submission.url)
                post_collection['Sentiment score'].append(score)

        all_posts = pd.DataFrame(post_collection)

        all_posts['Created at'] = pd.to_datetime(all_posts['Created at'], unit='s', utc=True)

        if self.log == 3:
            print(f'\n\nAll posts from {chosen_subreddit} subreddit:\n')
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            print(all_posts)
            pd.reset_option('display.max_rows')
            pd.reset_option('display.max_columns')

        self.all_posts_from_topic_subreddit = all_posts



    def get_posts_from_financial_subreddits(self, comments):
        if self.log == 2 or self.log == 3:
            print('\n\n\n\nPosts from the following subreddits: \nstocks\nStockMarket\nwallstreetbets\ninvesting')
        choosen_subreddit = self.topic_subreddit_decider('finance subreddit')
        post_collection = {"Title": [], "Subreddit": [], "Post Text": [], "Upvote Ratio": [],"Number of comments": [], "Created at": [], "Post URL": [], "Sentiment score": []}

        for submission in self.reddit.subreddit("stocks+StockMarket+wallstreetbets+investing").search(query=choosen_subreddit, sort="new", time_filter="all"):
            good_submission, score = self.go_through_posts(submission, comments)
            if good_submission is not None and score is not None:
                post_collection["Title"].append(good_submission.title)
                post_collection['Subreddit'].append(good_submission.subreddit)
                post_collection["Post Text"].append(good_submission.selftext)
                post_collection["Upvote Ratio"].append(good_submission.upvote_ratio)
                post_collection["Number of comments"].append(good_submission.num_comments)
                post_collection["Created at"].append(good_submission.created_utc)
                post_collection["Post URL"].append(good_submission.url)
                post_collection['Sentiment score'].append(score)


        all_posts = pd.DataFrame(post_collection)

        all_posts['Created at'] = pd.to_datetime(all_posts['Created at'], unit='s', utc=True)

        if self.log == 3:
            print('\n\nAll posts from financial subreddits:\n')
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

        elif self.all_posts_from_topic_subreddit.empty and self.all_posts_from_financial_subreddit.empty:
            print("Both dataframes are empty.")
        elif self.all_posts_from_topic_subreddit.empty:
            print("Topic subreddit dataframe is empty. Using financial subreddit dataframe.")
            self.merged_posts = self.all_posts_from_financial_subreddit
        elif self.all_posts_from_financial_subreddit.empty:
            print("Financial subreddit dataframe is empty. Using topic subreddit dataframe.")
            self.merged_posts = self.all_posts_from_topic_subreddit

        if self.log == 2 or self.log == 3:
            print('\n\nMerged posts:\n')
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            print(self.merged_posts)
            pd.reset_option('display.max_rows')
            pd.reset_option('display.max_columns')






    def data_into_hourly_averages(self):  # NEM JÓ TELJESEN !!!!!! - most már igen :)
        if self.merged_posts.empty:
            print("No data to process into hourly averages.")
            return

        self.merged_posts.set_index('Created at', inplace = True)

        #first_timestamp = self.merged_posts.index.min()
        #self.hourly_sentiment = self.merged_posts['Sentiment score'].resample('h', origin = first_timestamp).mean()
        self.hourly_sentiment = self.merged_posts['Sentiment score'].resample('h').mean()

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

        self.score_list = self.hourly_sentiment









#scraper = Reddit_Scraper('AAPL', '2024-09-08', '2024-09-09', 3)
#scraper.collect_from_reddit()
