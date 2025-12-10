from megamoots.v2_gpu_oracle.oracle_impl import PriceOracle
def test_oracle_basic():
    o = PriceOracle(window_seconds=60)
    o.ingest("aws","A100",3.2, ts=1)
    o.ingest("gcp","A100",2.8, ts=2)
    best = o.find_best("A100")
    assert best["cloud"] == "gcp"
