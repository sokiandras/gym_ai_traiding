import openai
#from openai import OpenAI
import requests
import google.generativeai as genai
import statistics
import time

class AI():
    def __init__(self, api_type):
        self.api_type = api_type

        self.api_key = 0
        if self.api_type == 'OpenAI':
            self.api_key = open("OPENAI_API_KEY.txt","r").read()

        elif self.api_type == 'Pawan_Osman':
            self.api_key = open("Pawan_Osman_API_KEY.txt", "r").read()
            #openai.api_base = 'https://api.pawan.krd/v1'
            openai.api_base = 'https://api.pawan.krd/pai-001-light-beta/v1'
            #openai.api_base = 'https://api.pawan.krd/v1/chat/completions'

        elif self.api_type == 'Gemini':
            self.api_key = open("Google_Gemini_API_KEY.txt", "r").read()
            genai.configure (api_key = self.api_key)

        elif self.api_type == 'OpenAI_4o':
            self.api_type = open('gpt_49_key.txt''r').read()

        openai.api_key = self.api_key



    def chat(self,message):

        if self.api_type == "OpenAI":
            # response = openai.ChatCompletion.create(
            #     model ="gpt-3.5-turbo",
            #     messages = [{"role": "user", "content": message}]
            # )
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": message}]
            )
            response_message = response['choices'][0]['message']['content']

            total_tokens = response['usage']['total_tokens']
            cost = total_tokens * 0.004 / 1000  # 1000 token ára 0,004 usd



        if self.api_type == 'OpenAI_4o':
            client = OpenAI(
                organisation ='org-K8gxZ6DRurWmIuEkRMGMPej1',
                project='proj_WRGIVD3vgYodfW4ALBHpFgbD'
            )
            completion = client.chat.completions.create(
                model ="gpt-4o",
                message = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )
            response = completion.choices[0].message



        elif self.api_type =='Pawan_Osman':
            response = openai.ChatCompletion.create(
                model="pai-001-beta",
                messages=[{"role": "user", "content": message}]
            )
            # response = openai.ChatCompletion.create(
            #     model="gpt-3.5-turbo",
            #     messages=[{"role": "user", "content": message}]
            # )
            response_message = response['choices'][0]['message']['content']

            total_tokens = response['usage']['total_tokens']
            cost = total_tokens * 0.004 / 1000  # 1000 token ára 0,004 usd



        elif self.api_type == "Gemini":
            generation_config = {
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
            ]
            #model = genai.GenerativeModel(model_name="gemini-1.0-pro", generation_config=generation_config, safety_settings=safety_settings)
            model = genai.GenerativeModel(model_name="gemini-1.5-flash-002", generation_config=generation_config, safety_settings=safety_settings)

            prompt_parts = [message]
            response = model.generate_content(prompt_parts)
            response_message = response.text
            total_tokens = 0
            cost = 0




        return response_message, total_tokens, cost




    def analyze_sentiment_chat(self,text):
        message = f"Please rate the sentiment of the following news article about a company: '{text}'. Use a discrete scale with whole numbers, where the minimum 0 means, that it is a very negative news about the company, and the maximum 10 means it is a very positive news for the company. Give back only a number and nothing else. No text!"
        response, tokens, cost = self.chat(message)

        return response






    def read_news_from_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        news_items = content.split('--')
        return [news.strip() for news in news_items if news.strip()]

    def analyze_news_file(self, file_path):
        news_items = self.read_news_from_file(file_path)
        index = 0
        results = []
        while index < len(news_items):
            text = news_items[index]
            response = self.analyze_sentiment_chat(text)
            try:
                score = float(response)
                results.append(score)
                #print(f"Sentiment Score: {score}\n")
            except ValueError:
                print(f"Invalid response: {response}\n")
            index += 1
            if self.api_type == "Pawan_Osman":
                time.sleep(5)

        if results:
            average_result = statistics.mean(results)
            print('Average result: ', average_result)
            print('\n')
        else:
            print('No valid sentiment scores to calculate average')




# ai = AI("OpenAI")


# message = "what does BNG in telco industry means?"
# response, total_tokens, cost = ai.chat(message)
#response = ai.analyze_sentiment_chat(message)
#print("Response: ", response)
# print("Tokens: ", total_tokens)
#print("Cost: ", cost, "USD")



# good_news_file = 'jó_hírek.txt'
# bad_news_file = 'rossz_hírek.txt'
# for i in range(0,5):
#     print("Analyzing good news:")
#     ai.analyze_news_file(good_news_file)
#
#     print("\nAnalyzing bad news:")
#     ai.analyze_news_file(bad_news_file)
#
#     print('\n-------------------\n')


#file_path = "D:\\Egyetem\\Önlab\\onlab2\\cikkek\\svb.txt"
#score = ai.analyze_sentiment_from_file(file_path)
#print(score)


