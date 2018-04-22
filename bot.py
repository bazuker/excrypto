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
    def progress_callback(n, p, g1, g2, total):
        if n == 1:
            Bot.clean_print(g1.id, "/", g2.id)
        print(n, 'out of', total, '|', p)
        time.sleep(0.05)
