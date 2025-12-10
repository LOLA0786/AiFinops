"""
Training Analyzer - improved parser + heuristic engine
- Parses common PyTorch / TF log lines
- Builds a scorecard and recommendations
"""
import re
def analyze_log(lines):
    issues = []
    joined = "\\n".join(lines)
    # OOM
    if re.search(r"cuda out of memory", joined, flags=re.I):
        issues.append("OOM")
    # dataloader slowness: 'DataLoader' with 'warning' or 'deadlock'
    if re.search(r"dataloader.*warning|dataloader.*deadlock", joined, flags=re.I):
        issues.append("DATALOADER_WARNING")
    # tiny batch sizes warning heuristic
    if re.search(r"batch_size[:=]\\s*(\\d+)", joined, flags=re.I):
        m = re.search(r"batch_size[:=]\\s*(\\d+)", joined, flags=re.I)
        if m and int(m.group(1)) < 8:
            issues.append("SMALL_BATCH")
    # gradient accumulation suggestion
    if re.search(r"grad_accum|accumulate_grad", joined, flags=re.I):
        issues.append("GRAD_ACCUM")
    return list(dict.fromkeys(issues))
