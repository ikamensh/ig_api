from src.robotrader.features.features import ExpAvg, WindowVariance, Pow

def expavg_stddev(window, smoothing):
    return Pow(ExpAvg(beta=smoothing, fn=WindowVariance(window)), 3/4)