"""
Autonomous Router - decision engine that balances cluster signature with price signals.
Policy:
- If avg_gpu_util < 15% -> scale down
- If cheapest cloud price is < threshold -> suggest migrate/spot scale option
- Provide safe actions with confidence scores
"""
def recommend_action(cluster_signature, price_signal, config=None):
    config = config or {}
    util = cluster_signature.get("avg_gpu_util",0)
    if util < config.get("scale_down_util_threshold",15):
        return {"action":"scale_down_nodes","confidence":0.9}
    # price_signal expected: {"cloud":..., "price":...}
    if price_signal and price_signal.get("price",999) < config.get("price_migrate_threshold",2.0):
        return {"action":"migrate_to_spot","target":price_signal["cloud"], "confidence":0.6}
    return {"action":"noop","confidence":0.1}
