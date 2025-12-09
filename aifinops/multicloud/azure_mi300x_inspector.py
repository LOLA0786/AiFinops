def fetch_mi300x_metrics(subscription_id):
    # ND MI300X SKUs detection pattern
    return [
        {"vm": "ND_Mi300x_112", "gpu_util": 0.22},
        {"vm": "ND_Mi300x_224", "gpu_util": 0.11}
    ]
