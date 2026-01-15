variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnets" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "master_username" {
  description = "DocumentDB master username"
  type        = string
  sensitive   = true
}

variable "master_password" {
  description = "DocumentDB master password"
  type        = string
  sensitive   = true
}

variable "instance_class" {
  description = "DocumentDB instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "security_group_id" {
  description = "DocumentDB security group ID"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
