resource "aws_docdb_cluster" "main" {
  cluster_identifier      = "${var.project_name}-${var.environment}-mongodb"
  engine                  = "docdb"
  master_username         = var.master_username
  master_password         = var.master_password
  db_subnet_group_name    = aws_docdb_subnet_group.main.name
  vpc_security_group_ids  = [var.security_group_id]
  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  skip_final_snapshot     = var.environment != "prod"
  storage_encrypted       = true
  enabled_cloudwatch_logs_exports = ["audit", "profiler"]

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-mongodb"
    }
  )
}

resource "aws_docdb_cluster_instance" "main" {
  count              = 1
  identifier         = "${var.project_name}-${var.environment}-mongodb-${count.index + 1}"
  cluster_identifier = aws_docdb_cluster.main.id
  instance_class     = var.instance_class

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-mongodb-instance-${count.index + 1}"
    }
  )
}

resource "aws_docdb_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-docdb-subnet-group"
  subnet_ids = var.private_subnets

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-docdb-subnet-group"
    }
  )
}
