

class packet:
    
    def __init__(self, seq_num: bytes, type: bytes, data: bytes):
        self.data = data
        self.type = type
        self.seq_num = seq_num