import hashlib
class Block:
    def __init__(self, prevBlockHash, transactionList):
        self.prevBlockHash = prevBlockHash
        self.transactionList = transactionList
        self.blockData = "-".join(self.transactionList) + "-" + self.prevBlockHash
        self.blockHash = hashlib.sha256(self.blockData.encode()).hexdigest()
