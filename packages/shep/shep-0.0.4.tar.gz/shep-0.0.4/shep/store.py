class SimpleStore:

    def __init__(self, path):
        self.path = path


    def add(self, k, v):
        fp = os.path.join(self.path, k, v)
        
