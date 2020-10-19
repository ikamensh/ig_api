class Instrument:

    def __init__(self, json_elem):
        self.epic = json_elem["epic"]
        self.expiry = json_elem["expiry"]
        self.name = json_elem["name"]

        self.lot_size = json_elem["lotSize"]
        self.unit = json_elem["unit"]
        self.type = json_elem["type"]

        self.market_id = json_elem["marketId"]
        assert json_elem["marginFactorUnit"] == "PERCENTAGE"
        self.margin = json_elem["marginFactor"] / 100
        self.currencies = json_elem["currencies"]

        self.country = json_elem["country"]
        self.contract_size = json_elem["contractSize"]
        self.news_code = json_elem["newsCode"]
