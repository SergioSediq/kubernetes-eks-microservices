variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "cluster_oidc_provider_arn" {
  description = "EKS cluster OIDC provider ARN"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
