def translate_job_to_order(job):
    return {
        "gpu": job["gpu"],
        "price": job.get("max_price", 1.0),
        "amount": job["hours"]
    }
