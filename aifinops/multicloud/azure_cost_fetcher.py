from azure.identity import DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient
import datetime as dt

def fetch_azure_costs(days=3, subscription_id=None):
    credential = DefaultAzureCredential()
    client = CostManagementClient(credential)

    since = (dt.datetime.utcnow() - dt.timedelta(days=days)).strftime("%Y-%m-%d")
    query = {
        "type": "Usage",
        "timeframe": "Custom",
        "timePeriod": {"from": since, "to": dt.datetime.utcnow().strftime("%Y-%m-%d")},
        "dataset": {"granularity": "Daily", "aggregation": {"totalCost": {"name": "Cost", "function": "Sum"}}}
    }

    results = client.query.usage(f"/subscriptions/{subscription_id}", query)

    rows = []
    for item in results.rows:
        rows.append({
            "date": item[0],
            "service": item[1],
            "cost": float(item[2])
        })

    return rows
