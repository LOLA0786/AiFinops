"""
Carbon optimizer:
- Score regions by renewable_pct and avg carbon intensity
"""
def score_region(region_info):
    # higher renewable_pct, lower carbon_intensity -> better score (lower)
    renewable_factor = max(0.0, min(1.0, region_info.get("renewable_pct",0)/100.0))
    intensity = region_info.get("carbon_intensity", 400)  # gCO2/kWh
    # score normalized [0,1] smaller is better
    score = (1.0 - renewable_factor) + (intensity / 1000.0)
    return score
