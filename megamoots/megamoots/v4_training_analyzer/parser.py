def analyze_log(lines):
    issues = []
    for l in lines:
        low = l.lower()
        if "cuda out of memory" in low:
            issues.append("OOM")
        if "dataloader" in low and "warning" in low:
            issues.append("dataloader_warning")
    return issues
