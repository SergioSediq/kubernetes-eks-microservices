variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "multi-tier-eks"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# EKS Cluster variables
variable "cluster_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
}

variable "node_instance_types" {
  description = "EC2 instance types for EKS node groups"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_desired_size" {
  description = "Desired number of nodes in node group"
  type        = number
  default     = 3
}

variable "node_min_size" {
  description = "Minimum number of nodes in node group"
  type        = number
  default     = 3
}

variable "node_max_size" {
  description = "Maximum number of nodes in node group"
  type        = number
  default     = 10
}

# PostgreSQL variables
variable "postgres_db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "appdb"
  sensitive   = true
}

variable "postgres_db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "postgres_db_password" {
  description = "PostgreSQL master password"
  type        = string
  sensitive   = true
}

variable "postgres_instance_class" {
  description = "PostgreSQL RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "postgres_allocated_storage" {
  description = "PostgreSQL allocated storage in GB"
  type        = number
  default     = 20
}

# MongoDB/DocumentDB variables
variable "mongodb_username" {
  description = "MongoDB master username"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "mongodb_password" {
  description = "MongoDB master password"
  type        = string
  sensitive   = true
}

variable "mongodb_instance_class" {
  description = "DocumentDB instance class"
  type        = string
  default     = "db.t3.medium"
}

# Redis variables
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.micro"
}
