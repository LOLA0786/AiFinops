from megamoots.gpu_oracle.oracle import find_best

def test_find_best():
    assert find_best('A100') is not None
