import re


class Numeric:
    def __init__(self, text):
        self.text = text
        self.remove_num()

    def remove_num(self):
        self.text = re.sub(r'\d+', ' ', self.text)
        self.text = re.sub(r'\s+', ' ', self.text)
        return self.text