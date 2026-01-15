resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-redis-subnet-group"
  subnet_ids = var.private_subnets

  tags = var.tags
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${var.project_name}-${var.environment}-redis"
  description                = "Redis cluster for ${var.project_name}"
  node_type                  = var.node_type
  port                       = 6379
  parameter_group_name       = "default.redis7"
  num_cache_clusters         = 2
  automatic_failover_enabled = true
  multi_az_enabled           = true
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  security_group_ids          = [var.security_group_id]
  at_rest_encryption_enabled  = true
  transit_encryption_enabled  = true

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-redis"
    }
  )
}
