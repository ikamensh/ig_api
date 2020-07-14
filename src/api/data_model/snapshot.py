class Snapshot:
    def __init__(self, json_elem):
        self.status = json_elem["marketStatus"]
        self.net_change = json_elem["netChange"]
        self.percentage_change = json_elem["percentageChange"]
        self.update_time = json_elem["updateTime"]
        self.delay_time = json_elem["delayTime"]
        self.bid = json_elem["bid"]
        self.offer = json_elem["offer"]
        self.low = json_elem["low"]
        self.high = json_elem["high"]

        if self.offer is None or self.bid is None:  # TODO raise exception instead
            self.delta = None
        else:
            self.delta = self.offer - self.bid