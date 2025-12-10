def score_region(region_info):
    # placeholder: lower is better
    return region_info.get("renewable_pct",0) * 0.01
