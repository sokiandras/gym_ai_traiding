import openai
import requests

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
        elif self.api_type =='NovaAI':
            self.api_key = open("NOVA_AI_API_KEY.txt", "r").read()
            openai.api_base = 'https://api.nova-oss.com/v1'

        openai.api_key = self.api_key



    def chat(self,message):

        if self.api_type == "OpenAI":
            response = openai.ChatCompletion.create(
                model ="gpt-3.5-turbo",
                messages = [{"role": "user", "content": message}]
            )

        elif self.api_type =='Pawan_Osman':
            response = openai.ChatCompletion.create(
                model="pai-001-beta",
                messages=[{"role": "user", "content": message}]
            )

        elif self.api_type =='NovaAI':
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": message}]
            )

        response_message = response['choices'][0]['message']['content']

        total_tokens = response['usage']['total_tokens']
        cost = total_tokens * 0.004 / 1000  # 1000 token ára 0,004 usd


        return response_message, total_tokens, cost




    def analyze_sentiment_chat(self,text):
        message = f"Please rate the sentiment of the following news article about a company: '{text}'. Use a discrete scale with whole numbers, where the minimum 0 means, that it is a very negative news about the company, and the maximum 10 means it is a very positive news for the company. Give back only a number and nothing else. No text!"
        response, tokens, cost = self.chat(message)

        return response




    def analyze_sentiment_from_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
            response_chat = self.analyze_sentiment_chat(text)
            print('chat response: ', response_chat,'\n')

            if(response_chat.isdigit()):
                score = int(response_chat)
            else:
                print('The response is not a digit')
                score = -1
            return score





#ai = AI("NovaAI")
#ai = AI("Pawan_Osman")
#ai = AI("OpenAI")
#message = "what does BNG in telco industry means?"
#response, total_tokens, cost = ai.chat(message)

#print("Response: ", response)
#print("Tokens: ", total_tokens)
#print("Cost: ", cost, "USD")


#file_path = "D:\\Egyetem\\Önlab\\onlab2\\cikkek\\svb.txt"
#score = ai.analyze_sentiment_from_file(file_path)
#print(score)


