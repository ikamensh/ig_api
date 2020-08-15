from typing import Dict


class AccountDetails:
    def __init__(self, balance, profit_loss, available, name, id, currency):
        self.balance = balance
        self.profit_loss = profit_loss
        self.available = available  # 1000$ gold -> 5% -> 50$
        self.name = name
        self.id = id
        self.currency = currency
    
        
    @staticmethod
    def from_json(json_elem: Dict):
        balance = float(json_elem["balance"]["balance"])
        profit_loss = json_elem["balance"]["profitLoss"]
        available = json_elem["balance"]["available"]
        name = json_elem["accountName"]
        id = json_elem["accountId"]
        currency = json_elem["currency"]

        return AccountDetails(balance, profit_loss, available, name, id, currency)

    def __repr__(self):
        return f"Account {self.id} | {self.name} with balance {self.balance} {self.currency}"