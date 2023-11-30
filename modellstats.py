import torch
from stockmarketenv import StockMarketEnv

class ModellStats():
    def __init__ (self,path):
        self.path = path

    def weights_and_biases(self):
        model = torch.load(self.path)
        params = model.state.dict()
        for name, param in params.items():
            print(f'Layer: {name}')
            if 'weight' in name:
                print('Weights:')
            elif 'bias' in name:
                print('Biases:')
            print(param)
            print('-------------------------')