output "cluster_id" {
  description = "DocumentDB cluster ID"
  value       = aws_docdb_cluster.main.id
}

output "endpoint" {
  description = "DocumentDB cluster endpoint"
  value       = aws_docdb_cluster.main.endpoint
  sensitive   = true
}

output "reader_endpoint" {
  description = "DocumentDB cluster reader endpoint"
  value       = aws_docdb_cluster.main.reader_endpoint
  sensitive   = true
}
