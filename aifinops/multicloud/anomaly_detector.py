import statistics as stats

def detect_multicloud_anomalies(costs):
    """
    costs = [
        {"provider": "aws", "date": "...", "cost": 12.3},
        {"provider": "gcp", ...},
        {"provider": "azure", ...}
    ]
    """
    by_provider = {}
    for c in costs:
        by_provider.setdefault(c["provider"], []).append(c["cost"])

    anomalies = []
    for provider, values in by_provider.items():
        if len(values) < 3:
            continue
        mean = stats.mean(values)
        stdev = stats.stdev(values)
        for idx, value in enumerate(values):
            if value > mean + 2 * stdev:
                anomalies.append({
                    "provider": provider,
                    "value": value,
                    "mean": mean,
                    "stddev": stdev,
                    "severity": "high"
                })

    return anomalies
