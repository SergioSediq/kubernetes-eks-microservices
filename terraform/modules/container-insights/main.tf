# CloudWatch Log Group for Container Insights
resource "aws_cloudwatch_log_group" "container_insights" {
  name              = "/aws/containerinsights/${var.cluster_name}/performance"
  retention_in_days = 7

  tags = var.tags
}

# IAM Role for CloudWatch Agent
data "aws_iam_policy_document" "cloudwatch_agent" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${replace(var.cluster_oidc_provider_arn, "/^(.*provider/)/", "")}:sub"
      values   = ["system:serviceaccount:amazon-cloudwatch:cloudwatch-agent"]
    }

    condition {
      test     = "StringEquals"
      variable = "${replace(var.cluster_oidc_provider_arn, "/^(.*provider/)/", "")}:aud"
      values   = ["sts.amazonaws.com"]
    }

    principals {
      identifiers = [var.cluster_oidc_provider_arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "cloudwatch_agent" {
  name               = "${var.cluster_name}-cloudwatch-agent"
  assume_role_policy = data.aws_iam_policy_document.cloudwatch_agent.json

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "cloudwatch_agent" {
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
  role       = aws_iam_role.cloudwatch_agent.name
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "container_insights" {
  dashboard_name = "${var.project_name}-${var.environment}-container-insights"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["ContainerInsights", "node_cpu_utilization", { "stat" = "Average" }],
            ["ContainerInsights", "node_memory_utilization", { "stat" = "Average" }],
            ["ContainerInsights", "node_network_total_bytes", { "stat" = "Sum" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = "us-east-1"
          title   = "Node Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["ContainerInsights", "pod_cpu_utilization", { "stat" = "Average" }],
            ["ContainerInsights", "pod_memory_utilization", { "stat" = "Average" }],
            ["ContainerInsights", "pod_network_rx_bytes", { "stat" = "Sum" }],
            ["ContainerInsights", "pod_network_tx_bytes", { "stat" = "Sum" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = "us-east-1"
          title   = "Pod Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["ContainerInsights", "cluster_failed_node_count", { "stat" = "Average" }],
            ["ContainerInsights", "cluster_node_count", { "stat" = "Average" }],
            ["ContainerInsights", "service_number_of_running_pods", { "stat" = "Average" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = "us-east-1"
          title   = "Cluster Metrics"
          period  = 300
        }
      }
    ]
  })
}
