def detect_arbitrage(prices):
    opps = []
    for gpu in ["A100","H100","L4","MI300X"]:
        quotes = [(p, prices[p][gpu]) for p in prices if gpu in prices[p]]
        if not quotes: continue
        low_p, low = min(quotes, key=lambda x: x[1])
        high_p, high = max(quotes, key=lambda x: x[1])
        if high - low > 0.25:
            opps.append({"gpu": gpu, "buy": low_p, "sell": high_p, "profit": high - low})
    return opps
