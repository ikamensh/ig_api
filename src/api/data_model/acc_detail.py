class AccountDetails:
    def __init__(self, json_elem):
        self.balance = float(json_elem["balance"]["balance"])
        self.name = json_elem["accountName"]
        self.id = json_elem["accountId"]
        self.currency = json_elem["currency"]
        self.profit_loss = json_elem["balance"]["profitLoss"]

    def __repr__(self):
        return f"Account {self.id} | {self.name} with balance {self.balance} {self.currency}"