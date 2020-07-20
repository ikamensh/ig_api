
class MarketId:
    def __init__(self, name, code):
        self.name = name
        self.code = code


# VIX = "CC.D.VIX.UNC.IP"  # large lot market

US500 = "IX.D.SPTRD.IFE.IP"
DAX30 = "IX.D.DAX.IFMM.IP"
GOLD = "CS.D.CFEGOLD.CFE.IP"
TSLA = "UD.D.TSLA.CASH.IP"

VIX = "CC.D.VIX.UME.IP"
VIX_EU = "CC.D.VSTOXX.UNC.IP"

vix = MarketId("vix", VIX)
vix_eu = MarketId("vix_eu", VIX_EU)
us500 = MarketId("us500", US500)
vix_official = MarketId("vix_official", None)
