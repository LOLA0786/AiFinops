provider "aws" {
  region = var.region
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.2.1"

  cluster_name = "${var.project_name}-eks-${var.env}"

  eks_managed_node_groups = {
    gpu = {
      instance_types = ["g4dn.xlarge", "g5.xlarge", "p4d.24xlarge"]
      desired_size   = 1
    }
  }
}
