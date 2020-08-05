from src.robotrader.features.features import ExpAvg, WindowVariance, Pow

def expavg_stddev(window):
    return Pow(fn=WindowVariance(window), pow=0.5)