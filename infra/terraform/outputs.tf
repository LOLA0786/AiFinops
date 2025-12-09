output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "api_url" {
  value = aws_ecs_service.api_service.id
}
