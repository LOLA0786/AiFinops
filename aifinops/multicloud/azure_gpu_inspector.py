from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

def fetch_azure_gpu_metrics(subscription_id=None):
    credential = DefaultAzureCredential()
    client = ComputeManagementClient(credential, subscription_id)

    results = []
    for vm in client.virtual_machines.list_all():
        if vm.hardware_profile.vm_size.startswith("Standard_N"):
            results.append({
                "vm": vm.name,
                "gpu": vm.hardware_profile.vm_size,
                "state": vm.instance_view.statuses[-1].display_status
            })
    return results
