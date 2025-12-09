from google.cloud import monitoring_v3
import datetime as dt

def fetch_gcp_gpu_metrics(project_id=None):
    client = monitoring_v3.MetricServiceClient()
    now = dt.datetime.utcnow()
    interval = monitoring_v3.TimeInterval({
        "end_time": now,
        "start_time": now - dt.timedelta(minutes=30)
    })

    gpu_metric = 'compute.googleapis.com/instance/gpu/utilization'
    results = []

    request = monitoring_v3.ListTimeSeriesRequest(
        name=f"projects/{project_id}",
        filter=f'metric.type="{gpu_metric}"',
        interval=interval,
        view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
    )

    for ts in client.list_time_series(request):
        instance = ts.resource.labels.get("instance_id")
        util = ts.points[0].value.double_value
        results.append({"instance": instance, "util": util})

    return results
