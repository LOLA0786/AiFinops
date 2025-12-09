provider "azurerm" {
  features {}
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = "${var.project_name}-aks-${var.env}"
  location            = var.region
  resource_group_name = "${var.project_name}-rg"
  dns_prefix          = "aifinopsgpucluster"

  default_node_pool {
    name       = "gpu"
    vm_size    = "Standard_ND96isr_H100_v5" # H100
    node_count = 1
  }
}
