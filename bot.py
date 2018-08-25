import os
import time


class Bot:

    def __init__(self, gateways, pairs):
        self.gateways = gateways
        self.pairs = pairs

    @staticmethod
    def clean_print(*args):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(*args)

    @staticmethod
    def progress_callback(g1, g2, temp_deals):
        Bot.clean_print(g1.id, "/", g2.id + "...", len(temp_deals))
        time.sleep(0.05)
