resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-${var.environment}-postgres"
  engine         = var.engine
  engine_version = var.engine_version
  instance_class = var.db_instance_class

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.allocated_storage * 2
  storage_type          = "gp3"
  storage_encrypted      = true

  db_subnet_group_name   = var.db_subnet_group_name != "" ? var.db_subnet_group_name : (length(aws_db_subnet_group.main) > 0 ? aws_db_subnet_group.main[0].name : "")
  vpc_security_group_ids = [var.security_group_id]

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  performance_insights_enabled    = true
  performance_insights_retention_period = 7

  skip_final_snapshot       = var.environment != "prod"
  final_snapshot_identifier = var.environment == "prod" ? "${var.project_name}-${var.environment}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-postgres"
    }
  )
}

resource "aws_db_subnet_group" "main" {
  count      = var.db_subnet_group_name == "" ? 1 : 0
  name       = "${var.project_name}-${var.environment}-postgres-subnet-group"
  subnet_ids = var.private_subnets

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-postgres-subnet-group"
    }
  )
}
