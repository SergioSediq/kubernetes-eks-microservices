terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }

  backend "s3" {
    # Configure backend in terraform.tfvars or via environment variables
    # bucket = "your-terraform-state-bucket"
    # key    = "kubernetes-eks/terraform.tfstate"
    # region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "kubernetes-eks-microservices"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  project_name     = var.project_name
  environment      = var.environment
  vpc_cidr         = var.vpc_cidr
  availability_zones = slice(data.aws_availability_zones.available.names, 0, 3)
  
  enable_nat_gateway = true
  enable_vpn_gateway  = false

  tags = local.common_tags
}

# EKS Cluster Module
module "eks" {
  source = "./modules/eks"

  project_name    = var.project_name
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnets
  public_subnets  = module.vpc.public_subnets

  cluster_version = var.cluster_version
  node_instance_types = var.node_instance_types
  node_desired_size = var.node_desired_size
  node_min_size     = var.node_min_size
  node_max_size     = var.node_max_size

  tags = local.common_tags
}

# RDS PostgreSQL Module
module "rds_postgres" {
  source = "./modules/rds"

  project_name    = var.project_name
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.database_subnets
  db_name         = var.postgres_db_name
  db_username     = var.postgres_db_username
  db_password     = var.postgres_db_password
  db_instance_class = var.postgres_instance_class
  allocated_storage = var.postgres_allocated_storage
  engine           = "postgres"
  engine_version   = "15.4"
  db_subnet_group_name = module.vpc.database_subnet_group_id

  security_group_id = module.security_groups.rds_security_group_id

  tags = local.common_tags
}

# DocumentDB (MongoDB) Module
module "documentdb" {
  source = "./modules/documentdb"

  project_name    = var.project_name
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.database_subnets
  master_username = var.mongodb_username
  master_password = var.mongodb_password
  instance_class  = var.mongodb_instance_class

  security_group_id = module.security_groups.documentdb_security_group_id

  tags = local.common_tags
}

# ElastiCache Redis Module
module "redis" {
  source = "./modules/redis"

  project_name    = var.project_name
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnets
  node_type       = var.redis_node_type

  security_group_id = module.security_groups.redis_security_group_id

  tags = local.common_tags
}

# Security Groups Module
module "security_groups" {
  source = "./modules/security-groups"

  vpc_id = module.vpc.vpc_id
  environment = var.environment
  project_name = var.project_name

  tags = local.common_tags
}

# Update EKS cluster security group
resource "aws_security_group_rule" "eks_cluster_from_nodes" {
  type                     = "ingress"
  from_port                 = 443
  to_port                   = 443
  protocol                  = "tcp"
  source_security_group_id  = module.eks.cluster_security_group_id
  security_group_id        = module.security_groups.eks_cluster_security_group_id
  description               = "Allow EKS nodes to communicate with cluster"
}

# ALB Ingress Controller
module "alb_ingress" {
  source = "./modules/alb-ingress"

  cluster_name = module.eks.cluster_name
  cluster_oidc_provider_arn = module.eks.cluster_oidc_provider_arn
  vpc_id = module.vpc.vpc_id

  tags = local.common_tags
}

# CloudWatch Container Insights
module "container_insights" {
  source = "./modules/container-insights"

  cluster_name = module.eks.cluster_name
  cluster_oidc_provider_arn = module.eks.cluster_oidc_provider_arn
  environment  = var.environment
  project_name = var.project_name

  tags = local.common_tags
}

# Kubernetes Provider
provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      module.eks.cluster_name
    ]
  }
}

# Helm Provider
provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args = [
        "eks",
        "get-token",
        "--cluster-name",
        module.eks.cluster_name
      ]
    }
  }
}

# Local values
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
