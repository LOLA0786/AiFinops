"""
Data Flywheel scaffold

Goals:
- Anonymize & aggregate cost patterns + GPU logs
- Store aggregated features for model training
- Provide API to export training datasets
- Privacy-first: strip PII, use hashing for identifiers

TODO:
- Wire to your storage (S3, GCS or DB)
- Add schedule to aggregate daily snapshots
"""

import hashlib
import json
import datetime as dt
from typing import Dict, Any, List

def anonymize_resource_id(resource_id: str) -> str:
    """Deterministic hashing of resource ids so we can group without revealing IDs."""
    h = hashlib.sha256(resource_id.encode()).hexdigest()
    return "r_" + h[:16]

def aggregate_cost_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    rows: [{"date":"2025-12-09","account":"1234","service":"EC2","resource_id":"i-...","cost":12.3, ...}, ...]
    returns aggregated features per anonymized resource / daily bucket
    """
    agg = {}
    for r in rows:
        rid = anonymize_resource_id(r.get("resource_id","unknown"))
        key = (rid, r.get("service","unknown"))
        if key not in agg:
            agg[key] = {"resource_hash": rid, "service": r.get("service"), "cost_sum":0.0, "count":0, "dates":[]}
        agg[key]["cost_sum"] += float(r.get("cost",0.0))
        agg[key]["count"] += 1
        agg[key]["dates"].append(r.get("date"))
    # convert list to serializable
    return {k[0] + ":" + k[1]: v for k,v in agg.items()}

def export_dataset(aggregated: Dict[str,Any], out_path: str):
    """Write aggregated dataset for model training (parquet/csv as you prefer)."""
    with open(out_path, "w") as f:
        json.dump({"generated_at": dt.datetime.utcnow().isoformat(), "data": aggregated}, f)
    return out_path

# Example: how to call
if __name__ == "__main__":
    sample = [{"date":"2025-12-09","resource_id":"i-abc","service":"EC2","cost":10.0},
              {"date":"2025-12-09","resource_id":"i-abc","service":"EC2","cost":2.0}]
    agg = aggregate_cost_rows(sample)
    print(export_dataset(agg, "dataflywheel_sample.json"))
