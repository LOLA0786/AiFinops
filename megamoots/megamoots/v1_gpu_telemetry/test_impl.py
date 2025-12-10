from megamoots.v1_gpu_telemetry.telemetry_impl import SimAdapter, TelemetryPublisher
def test_sim_adapter_and_publish(tmp_path):
    adapter = SimAdapter(node_id="t", seed=0)
    pub = TelemetryPublisher(out_path=str(tmp_path/"q.jsonl"), batch=2)
    run_count = 3
    # publish a few samples
    for _ in range(run_count):
        s = adapter.sample_once()[0]
        pub.publish(s)
    pub.flush()
    with open(str(tmp_path/"q.jsonl")) as f:
        lines = f.readlines()
    assert len(lines) >= 1
