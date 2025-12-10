def suggest_changes(bill, metrics):
    # placeholder: naive rule
    if bill.get("monthly",0) > 10000:
        return ["reduce_nodes", "use_spot"]
    return []
