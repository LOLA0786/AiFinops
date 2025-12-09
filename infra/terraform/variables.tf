variable "region" {
  default = "us-east-1"
}

variable "api_image" {
  description = "ECR or DockerHub image for AiFinOps API server"
}

variable "token_secret" {
  description = "Secret used to sign API tokens"
}
