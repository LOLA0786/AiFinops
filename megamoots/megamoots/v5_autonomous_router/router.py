def recommend_action(cluster_signature, price_signal):
    if cluster_signature.get("avg_gpu_util",0) < 10:
        return {"action":"scale_down_nodes"}
    return {"action":"no_op"}

if __name__=="__main__":
    print(recommend_action({"avg_gpu_util":5},("gcp",2.9)))
