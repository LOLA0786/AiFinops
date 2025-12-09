provider "google" {
  project = var.project_name
  region  = var.region
}

resource "google_container_cluster" "gke" {
  name                     = "${var.project_name}-gke-${var.env}"
  location                 = var.region
  remove_default_node_pool = true
}

resource "google_container_node_pool" "gpu_pool" {
  name       = "gpu-pool"
  location   = var.region
  cluster    = google_container_cluster.gke.name

  node_config {
    machine_type = "a2-highgpu-1g" # A100
    guest_accelerator {
      type  = "nvidia-tesla-a100"
      count = 1
    }
  }
}
