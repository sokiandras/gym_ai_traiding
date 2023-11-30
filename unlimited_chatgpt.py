from pyChatGPT import ChatGPT

class U_AI():
    def __init__(self):
        self.session_token = open("ChatGPT_session_key.txt","r").read()
        self.api = ChatGPT(self.session_token)

    def get(self):
        resp = self.api.send_message("How to write a python program that uses chatgpt?")
        print(resp['message'])




test = U_AI()
test.get()
