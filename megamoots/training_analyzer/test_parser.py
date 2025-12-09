from megamoots.training_analyzer.parser import analyze_log

def test_analyze():
    logs = ["CUDA out of memory", "DataLoader warning detected"]
    issues = analyze_log(logs)
    assert "OOM" in issues
