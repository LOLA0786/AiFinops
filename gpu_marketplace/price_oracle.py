import requests

def get_aws_prices():
    # mocked simplified API
    return {"A100": 2.79, "H100": 4.10, "L4": 0.40}

def get_gcp_prices():
    return {"A100": 2.48, "L4": 0.35, "TPU-v5e": 1.90}

def get_azure_prices():
    return {"MI300X": 3.90, "H100": 4.20}

def aggregate():
    return {
        "aws": get_aws_prices(),
        "gcp": get_gcp_prices(),
        "azure": get_azure_prices(),
    }
