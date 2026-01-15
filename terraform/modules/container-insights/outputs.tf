output "log_group_name" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.container_insights.name
}

output "iam_role_arn" {
  description = "IAM role ARN for CloudWatch agent"
  value       = aws_iam_role.cloudwatch_agent.arn
}
