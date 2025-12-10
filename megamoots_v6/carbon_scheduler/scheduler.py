import random

def carbon_optimize(job_name):
    low_carbon_hours = random.randint(1,6)
    recommendation = f"Delay {job_name} by {low_carbon_hours}h to run on low-carbon window"
    carbon_savings = round(random.uniform(0.5,3.4), 2)
    return {
        "recommendation": recommendation,
        "carbon_savings_tons": carbon_savings
    }
