import json
import datetime as dt
from google.cloud import bigquery

def fetch_gcp_daily_costs(days=3, project_id=None, dataset="billing", table="gcp_billing_export"):
    client = bigquery.Client(project=project_id)
    since = (dt.datetime.utcnow() - dt.timedelta(days=days)).strftime("%Y-%m-%d")

    query = f"""
    SELECT
        DATE(usage_start_time) AS date,
        service.description AS service,
        SUM(cost) AS cost
    FROM `{project_id}.{dataset}.{table}`
    WHERE DATE(usage_start_time) >= DATE('{since}')
    GROUP BY date, service
    ORDER BY date DESC
    """

    rows = client.query(query).result()

    results = []
    for r in rows:
        results.append({
            "date": str(r.date),
            "service": r.service,
            "cost": float(r.cost)
        })
    return results
