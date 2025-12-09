def build_multicloud_pr(anomalies):
    lines = ["# AiFinOps Multi-Cloud Optimization PR\n"]
    for a in anomalies:
        cloud = a["provider"]
        if cloud == "aws":
            fix = "- Convert GPU EC2 instances to Spot where safe\n"
        elif cloud == "gcp":
            fix = "- Right-size GKE GPU nodepool or scale to zero\n"
        elif cloud == "azure":
            fix = "- Resize MI300X/ND-series GPU VMs to optimal tier\n"
        else:
            fix = "- Unknown provider\n"

        lines.append(f"## {cloud.upper()} anomaly\n")
        lines.append(f"Detected spike: {a['value']}\n")
        lines.append(f"Recommended fix:\n{fix}")

    return "\n".join(lines)
