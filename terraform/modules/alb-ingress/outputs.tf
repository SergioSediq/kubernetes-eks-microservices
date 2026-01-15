output "iam_role_arn" {
  description = "IAM role ARN for ALB Ingress Controller"
  value       = aws_iam_role.alb_ingress.arn
}
