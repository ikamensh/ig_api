
class Market:
    def __init__(self, name, code):
        self.name = name
        self.code = code


US500 = "IX.D.SPTRD.IFE.IP"
DAX30 = "IX.D.DAX.IFMM.IP"

GOLD = "CS.D.CFEGOLD.CFE.IP"

# VIX = "CC.D.VIX.UNC.IP"
VIX = "CC.D.VIX.UME.IP"

VIX_EU = "CC.D.VSTOXX.UNC.IP"

TSLA = "UD.D.TSLA.CASH.IP"

vix = Market("ig_vix", VIX)
