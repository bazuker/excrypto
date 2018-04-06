from pathlib import Path
import json


class SymbolFilter():
    def __init__(self):
        self.data = None

    # return a new list of matching strings from two lists
    def match_pairs(self, pairs1, pairs2):
        pairs = []
        dic = {}
        for p in pairs1:
            dic[p] = 1
        for p in pairs2:
            if p in dic:
                pairs.append(p)
        return pairs

    # returns only allowed currencies from the file
    def split_pairs(self, pairs):
        # load the currencies file if it exists
        if self.data is None:
            currencies_filename = 'currencies.json'
            currencies_file = Path(currencies_filename)
            self.data = None
            if currencies_file.is_file():
                self.data = json.load(open(currencies_filename))
            else:
                raise Exception('file currencies.json is not found!')
        # split all the pairs
        available_pairs = []
        for p in pairs:
            # prefix
            for prefix in self.data:
                prefix_len = len(prefix)
                if p[:prefix_len] == prefix:
                    # suffix
                    for suffix in self.data:
                        if p[prefix_len:] == suffix:
                            available_pairs.append([prefix, suffix])
        # return the new filtered list
        return available_pairs
