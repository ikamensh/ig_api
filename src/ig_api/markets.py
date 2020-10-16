class MarketId:
    def __init__(self, code, name = None):
        """
        Args:
            code: market code used on ig.com platform. Use https://labs.ig.com/sample-apps/api-companion/index.html to find more codes.
            name: optional, human-friendly name of the market.
        """
        self.code = code
        self.name = name or code

    def __repr__(self):
        return f"MarketId({self.code=}, {self.name=} at {hash(self)}"


# VIX = "CC.D.VIX.UNC.IP"  # large lot market

_US500 = "IX.D.SPTRD.IFE.IP"
_DAX30 = "IX.D.DAX.IFMM.IP"
_GOLD = "CS.D.CFEGOLD.CFE.IP"
_TSLA = "UD.D.TSLA.CASH.IP"

_VIX = "CC.D.VIX.UME.IP"
_VIX_EU = "CC.D.VSTOXX.UNC.IP"

vix = MarketId(_VIX, "vix")
vix_eu = MarketId(_VIX_EU, "vix_eu")
us500 = MarketId(_US500, "us500")
gold = MarketId(_GOLD, "gold")
cboe_vix = MarketId(None, "vix_cboe")
