from megamoots.v4_training_analyzer.parser_impl import analyze_log
def test_training_parser():
    lines = ["Epoch 1", "CUDA out of memory at step 3", "DataLoader warning detected", "batch_size=4"]
    issues = analyze_log(lines)
    assert "OOM" in issues and "DATALOADER_WARNING" in issues and "SMALL_BATCH" in issues
