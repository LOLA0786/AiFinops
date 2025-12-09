import os
from aifinops.aws_cost_fetcher import fetch_aws_daily_costs
from aifinops.multicloud.gcp_cost_fetcher import fetch_gcp_daily_costs
from aifinops.multicloud.azure_cost_fetcher import fetch_azure_costs

def fetch_multicloud_costs(provider, days=3):
    provider = provider.lower()

    if provider == "aws":
        return fetch_aws_daily_costs(days=days)

    if provider == "gcp":
        return fetch_gcp_daily_costs(days=days, project_id=os.getenv("GCP_PROJECT_ID"))

    if provider == "azure":
        return fetch_azure_costs(days=days, subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"))

    raise ValueError("Unknown provider: choose aws | gcp | azure")
