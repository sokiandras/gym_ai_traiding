import yfinance as yf
import pandas as pd
#from env_with_news import Env_with_news
from newsplease import NewsPlease

input_string = "1h"
numeric_value = int(input_string[:-1])

print(numeric_value)

symbol = "aapl"
start_date = "2024-03-28"
end_date = "2024-03-29"


testdata = yf.download(symbol, start=start_date, end=end_date, interval=input_string)


print("Testdata head: ")
pd.set_option('display.max_columns', None)
print(testdata.head(15))

print("All prices from testdata: ")
for i in range(len(testdata)):
    print("Price: ", testdata.iloc[i,0])


print("\n\nAll dates with prices from testdata with date: ")
for i in range(len(testdata)):
    print("Date: ", testdata.index[i])
    print("Price: ", testdata.iloc[i,0])


# Convert the datetime index to string
str_index = testdata.index.strftime('%Y-%m-%d %H')

# Print the modified index
print(str_index)



datalen = len(testdata)
print("\nLength of data: ", datalen)


article = NewsPlease.from_url("https://444.hu/2024/04/19/a-media-es-magyar-peter")
print('\n',article.maintext)


string1 = "\nEz a string eleje"
string2 = "Ez a string vege"
string = string1 + " " + string2
print(string)




#test_env = Env_with_news('AAPL', '2023-11-28', '2023-11-29', 100000, 1, '1h')
#test_env.news_analysis_in_given_interval()



# elif news_scores_length > data_length:
#     # Calculate the average of news_scores for the time intervals where there is no data at the beginning of the day
#     average_beginning_day = sum(self.news_scores[:9]) / 9 if news_scores_length > 9 else 0
#     self.reducated_news_scores.append(average_beginning_day)
#
#     # Use the corresponding news_scores for the time intervals where there is data
#     self.reducated_news_scores.extend(self.news_scores[9:17])
#
#     # Calculate the average of news_scores for the time intervals where there is no data at the end of the day
#     average_end_day = sum(self.news_scores[17:]) / 7 if news_scores_length > 17 else 0
#     self.reducated_news_scores.append(average_end_day)