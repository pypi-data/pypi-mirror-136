class LogStore:

    def __init__(self, path):
        self.path = path


    def add(self, v):
        fp = os.path.join(self.path, k, v)
        
