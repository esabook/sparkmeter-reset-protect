from .readJson import rJ

class setting:
    def __init__(self):
        self.Data =  rJ("settings.json").read()
       