terraform {
  required_version = ">=1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# --- VPC ---
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "aifinops-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.region}a", "${var.region}b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.3.0/24", "10.0.4.0/24"]
}

# --- EKS Cluster ---
module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  version         = "20.2.1"
  cluster_name    = "aifinops-eks"
  cluster_version = "1.30"

  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets

  # GPU Node Group
  eks_managed_node_groups = {
    gpu_nodes = {
      instance_types = ["g4dn.xlarge"]
      desired_size   = 1
      max_size       = 3
      min_size       = 1
      capacity_type  = "SPOT"
    }
  }
}

# --- API Server (Fargate) ---
resource "aws_ecs_cluster" "api_cluster" {
  name = "aifinops-api-cluster"
}

resource "aws_ecs_task_definition" "api_task" {
  family                   = "aifinops-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"

  container_definitions = jsonencode([
    {
      name  = "api"
      image = var.api_image
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "AIFINOPS_TOKEN_SECRET", value = var.token_secret }
      ]
    }
  ])
}

resource "aws_ecs_service" "api_service" {
  name            = "aifinops-api"
  cluster         = aws_ecs_cluster.api_cluster.id
  task_definition = aws_ecs_task_definition.api_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = module.vpc.public_subnets
    assign_public_ip = true
    security_groups = []
  }
}
