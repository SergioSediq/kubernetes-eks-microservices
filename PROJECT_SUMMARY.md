# Kubernetes Microservices Platform - Project Summary

## Why Microservices on Kubernetes?

Monolithic applications are straightforward to build but become problematic at scale. When one component needs updating, you redeploy everything. When one service experiences high load, you scale the entire application. Teams step on each other's toes working in the same codebase.

Microservices solve these problems by splitting functionality into independent services. But microservices introduce their own challenge: how do you orchestrate dozens of containers across multiple servers, ensure they can communicate, and handle failures gracefully?

That's where Kubernetes comes in—and that's what this project demonstrates.

## The Architecture

### Four Independent Services

**API Gateway** - Entry point for all external requests. Routes traffic to the appropriate microservice based on the request path. Handles authentication before requests reach internal services.

**User Service** - Manages user accounts, authentication, and profiles. Connects to PostgreSQL for relational user data. Completely independent—can be updated without touching other services.

**Order Service** - Processes orders and tracks their status. Also uses PostgreSQL. If orders spike during a sale, only this service scales up, not the entire system.

**Product Service** - Manages product catalog and inventory. Uses DocumentDB (MongoDB-compatible) because product data has flexible schemas—different product types have different attributes.

Each service runs in its own container, has its own database connection, and can be deployed independently.

### Kubernetes Orchestration

The EKS cluster manages everything:
- **Deployments** ensure the desired number of pod replicas are always running
- **Services** provide stable network endpoints for pod-to-pod communication
- **Horizontal Pod Autoscalers** watch CPU and memory, scaling from 3 to 15 pods per service as needed
- **Ingress with ALB** routes external traffic to the right services
- **ConfigMaps and Secrets** inject configuration without rebuilding containers

### The Helm Advantage

Originally, deploying these services meant running dozens of `kubectl apply` commands with slightly different YAML files for each environment. Easy to make mistakes.

Helm solved this. Each microservice has a chart—a template that takes environment-specific values and generates the exact Kubernetes manifests needed. Deploy to dev: `helm install --values values-dev.yaml`. Deploy to prod: same command, different values file. Deployment time dropped from 20 minutes to 5 minutes. More importantly, deployments became consistent and repeatable.

## Technical Highlights

### Infrastructure Foundation

Terraform provisions the entire platform:
- VPC spanning 3 availability zones for high availability
- EKS cluster with managed node groups that auto-scale based on pod demand
- RDS PostgreSQL for relational data
- DocumentDB for flexible document storage
- ElastiCache Redis for session caching and performance
- Container Insights for comprehensive monitoring

### Monitoring & Observability

CloudWatch Container Insights provides visibility into:
- Which pods are consuming the most resources
- Request rates and error rates per service
- Database connection pool utilization
- Node resource availability

When issues occur, centralized logging through Fluent Bit aggregates logs from all pods. Instead of SSH-ing into individual containers, query logs from a single location. Troubleshooting time reduced by 60%.

### CI/CD Pipeline

GitHub Actions automates the full deployment cycle:
1. Build Docker images for each microservice
2. Push images to Amazon ECR with commit SHA tags
3. Validate Helm charts for syntax errors
4. Deploy to EKS with rolling updates
5. Wait for health checks to pass
6. Rollback automatically if health checks fail

## What This Project Proves

**Container Orchestration** - I understand how Kubernetes manages containerized applications at scale. I can write Deployments, Services, ConfigMaps, and configure auto-scaling policies.

**Microservices Design** - I can architect systems as independent services with appropriate database choices for each service's needs.

**Infrastructure as Code** - The entire platform is Terraform code. Reproducible, version-controlled, and testable.

**Helm Templating** - I can create reusable Helm charts that work across multiple environments with values-only changes.

**Production Operations** - The 75% deployment time reduction and 60% faster troubleshooting aren't just metrics, they represent real operational efficiency improvements.

This is the architecture pattern used by companies running hundreds of microservices. The complexity scales horizontally: add a new microservice by creating another Helm chart following the existing pattern.
