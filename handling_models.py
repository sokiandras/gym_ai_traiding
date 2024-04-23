import env_with_news
import tkinter as tk
from tkinter import filedialog
from stable_baselines3 import PPO
from env_with_news import Env_with_news


class ModelHandler:
    def __init__(self, env, getnews, getindexes):
        self.model_path = None
        self.env = env
        self.getnews = getnews
        self.getindexes = getindexes



    def choose_model(self):
        root = tk.Tk()
        root.wm_withdraw()

        if self.getnews == 1 and self.getindexes == 0:
            base_folder = "D:\Egyetem\Diplomamunka\modells\modells_with_news_without_indexes"

        if self.getnews == 0 and self.getindexes == 0:
            base_folder = "D:\Egyetem\Diplomamunka\modells\modells_without_news_without_indexes"

        if self.getnews == 0 and self.getindexes == 1:
            base_folder = "D:\Egyetem\Diplomamunka\modells\modells_without_news_with_indexes"

        if self.getnews == 1 and self.getindexes == 1:
            base_folder = "D:\Egyetem\Diplomamunka\modells\modells_with_news_with_indexes"


        self.model_path = filedialog.askopenfilename(initialdir=base_folder)

        return self.get_model()




    def get_model(self):
        if self.model_path is None:
            print("\nNo model has benn chosen")
            return None

        model = PPO.load(self.model_path, env = self.env)
        return model




    def train(self, steps):
        other_env = Env_with_news('AAPL','2024-03-04','2024-03-06', 100000, 2, '1h', "learn")
        model_handler = ModelHandler(other_env)
        model_handler.choose_model()
        model = model_handler.get_model()