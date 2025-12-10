from megamoots.v1_gpu_telemetry.telemetry import TelemetryClient

def test_sample():
    c = TelemetryClient()
    p = c.sample()
    assert "gpu_util" in p
