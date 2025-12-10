from megamoots.v4_training_analyzer.parser import analyze_log

def test_analyze():
    lines = ["Epoch 1", "CUDA out of memory at step", "DataLoader warning"]
    issues = analyze_log(lines)
    assert "OOM" in issues
