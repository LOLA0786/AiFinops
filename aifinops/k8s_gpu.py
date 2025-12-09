from __future__ import annotations
import os
from typing import List, Dict
try:
    from kubernetes import client, config
    K8S_AVAILABLE = True
except Exception:
    K8S_AVAILABLE = False

def load_kube():
    if not K8S_AVAILABLE:
        raise RuntimeError("kubernetes package not available")
    # prefer in-cluster, fallback to local kubeconfig
    try:
        config.load_incluster_config()
    except Exception:
        kubeconfig = os.getenv('KUBECONFIG') or os.path.expanduser('~/.kube/config')
        config.load_kube_config(config_file=kubeconfig)

def list_gpu_pods(namespace: str = None) -> List[Dict]:
    """
    Returns list of pods that request GPUs (nvidia.com/gpu or amd.com/gpu).
    Each entry contains: pod_name, namespace, node_name, gpu_requests, containers list.
    """
    if not K8S_AVAILABLE:
        return []
    load_kube()
    v1 = client.CoreV1Api()
    ns = namespace if namespace else ''
    if ns:
        pods = v1.list_namespaced_pod(ns).items
    else:
        pods = v1.list_pod_for_all_namespaces().items
    result = []
    for p in pods:
        node = p.spec.node_name
        gpu_reqs = 0
        for c in p.spec.containers:
            if c.resources and c.resources.requests:
                for k,v in c.resources.requests.items():
                    if k.lower().endswith("gpu") or "nvidia.com/gpu" in k or "amd.com/gpu" in k:
                        try:
                            gpu_reqs += int(v)
                        except Exception:
                            gpu_reqs += 1
        if gpu_reqs > 0:
            result.append({
                "pod_name": p.metadata.name,
                "namespace": p.metadata.namespace,
                "node": node,
                "gpu_requests": gpu_reqs,
                "containers": [c.name for c in p.spec.containers],
                "phase": p.status.phase
            })
    return result

def map_nodes_with_gpus() -> List[Dict]:
    """Return nodes that advertise GPU allocatable capacity"""
    if not K8S_AVAILABLE:
        return []
    load_kube()
    v1 = client.CoreV1Api()
    nodes = v1.list_node().items
    out = []
    for n in nodes:
        alloc = n.status.allocatable or {}
        gpu = 0
        for k,v in alloc.items():
            if k.lower().endswith("gpu") or "nvidia.com/gpu" in k or "amd.com/gpu" in k:
                try:
                    gpu += int(v)
                except Exception:
                    gpu += 0
        out.append({"node": n.metadata.name, "gpu_allocatable": gpu})
    return out
