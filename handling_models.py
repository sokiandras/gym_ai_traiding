import env_with_news
import tkinter as tk
from tkinter import filedialog
from stable_baselines3 import PPO

class ModelHandler:
    def __init__(self, env):
        self.model_path = None
        self.env = env

    def choose_model(self):
        root = tk.Tk()
        root.wm_withdraw()
        base_folder = "D:\Egyetem\Diplomamunka\modells"
        self.model_path = filedialog.askopenfilename(initialdir=base_folder)


    def get_model(self):
        if self.model_path is None:
            print("\nNo model has benn chosen")
            return None

        model = PPO.load(self.model_path, env = self.env)
        return model
