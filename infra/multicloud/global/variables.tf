variable "env" { default = "prod" }
variable "region" { default = "us-east-1" }
variable "project_name" { default = "aifinops" }

# GPU SKU selection
variable "gpu_type" {
  default = "A100"
  description = "GPU type (A100, H100, L4, MI300X, TPU-v5e)"
}
