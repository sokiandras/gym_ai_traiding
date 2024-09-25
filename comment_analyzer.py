from vader_sentiment.vader_sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import torch
from statistics import mean
import time



class Comment_Analyzer():
    def __init__(self, log):
        #self.comments = comment
        self.log = log



    def hugging_face_loader(self, hugging_face_model_name, sentence):
        if self.log == 3:
            print(f"\nHuggingFace: {hugging_face_model_name} ")
        tokenizer = AutoTokenizer.from_pretrained(hugging_face_model_name)
        hugging_face_model = AutoModelForSequenceClassification.from_pretrained(hugging_face_model_name)


        #encoded_text = tokenizer(sentence, return_tensors='pt')
        encoded_text = tokenizer(sentence, return_tensors='pt', truncation=True, max_length=512)
        output = hugging_face_model(**encoded_text)

        return output




    def one_message_analyzer(self, sentence):
        #sentence = self.comments
        self.sentence = sentence

        # #if self.analyzer_type == 'TextBlob':
        # print('\nTextBlob: ')
        # result = TextBlob(sentence)
        # print(result.sentiment)
        #
        # #if self.analyzer_type == 'Vader':
        # print('\nVader:')
        # analyzer = SentimentIntensityAnalyzer()
        # result = analyzer.polarity_scores(sentence)
        # print(str(result))

        hugging_face_model_name1 = f"NazmusAshrafi/stock_twitter_sentiment_Bert"
        hugging_face_model_name2 = f"mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
        hugging_face_model_name3 = f"nlptown/bert-base-multilingual-uncased-sentiment"

        start_time = time.time()
        output1 = self.hugging_face_loader(hugging_face_model_name1, self.sentence)
        scores1 = output1[0][0].detach().numpy()
        scores1 = softmax(scores1)
        scores_dict1 = {
            'negative': scores1[0],
            'positive': scores1[1]
        }
        end_time = time.time()
        if self.log == 3:
            print(scores_dict1)
            print(f"Time taken: {end_time - start_time} s")
        result1 = scores1[1]
        if scores1[0] > scores1[1]:
            result1 = -scores1[0] #inkább negatív



        start_time = time.time()
        output2 = self.hugging_face_loader(hugging_face_model_name2, self.sentence)
        scores2 = output2.logits.detach().numpy()
        scores2 = softmax(scores2)
        scores_dict2 = {
            'negative': scores2[0][0],
            'neutral': scores2[0][1],
            'positive': scores2[0][2]
        }
        end_time = time.time()
        if self.log == 3:
            print(scores_dict2)
            print(f"Time taken: {end_time - start_time} s")
        result2 = scores2[0][2]
        if scores2[0][0] > scores2[0][2]:
            result2 = -scores2[0][0]


        start_time = time.time()
        output3 = self.hugging_face_loader(hugging_face_model_name3, self.sentence)
        scores3 = int(torch.argmax(output3.logits))+1
        if self.log == 3:
            print(scores3)
        if scores3 == 3:
            result3 = 0
        if scores3 > 3:
            result3 = scores3 / 5
        if scores3 == 2:
            result3 = - scores3 / 5
        if scores3 == 1:
            result3 = -1
        end_time = time.time()
        if self.log == 3:
            print(f"Time taken: {end_time - start_time} s")



        average_result = mean([float(result1), float(result2), float(result3)])
        result = (average_result + 1) * 5

        if self.log == 3:
            print(f"\nresult 1: {result1}, result 2: {result2}, result 3: {result3}")
            print(f"\nAverage score: {average_result}\n")
            print(f"\nResult from 0 to 10: {result}\n")

        return result







# sentence_good = "Thrilled to see #FictoCorp leading the charge with their innovative solutions and unwavering commitment to ethical business practices. With every milestone they hit, investors can rest easy knowing they're backing a company that's not just about profit, but about making a positive impact. 🌟💼 #EthicalLeadership #Innovation"
# sentence_bad = "Rumors swirling about #FictoCorp's shady practices and sketchy leadership have investors on edge. With scandals piling up, it's no wonder their stock prices are taking a nosedive. Time for some serious damage control or it's game over for this sinking ship. 💸📉 #Stocks #Scandal"
# sentence_slightly_good = "Despite recent challenges, #FictoCorp continues to demonstrate resilience and determination. With a solid foundation and a talented team, they're poised to bounce back stronger than ever. Here's to brighter days ahead! 🌟💼 #StayStrong #Recovery"
#
# test = Comment_Analyzer(2)
# average_result = test.one_message_analyzer(sentence_slightly_good)