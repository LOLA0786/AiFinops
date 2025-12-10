def choose_market(signals):
    # placeholder: pick lowest price signal
    best = min(signals, key=lambda s:s["price"])
    return best
