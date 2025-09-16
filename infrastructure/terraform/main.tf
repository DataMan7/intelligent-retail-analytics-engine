# 🏗️ Intelligent Retail Analytics Engine v3.0 - Infrastructure as Code
# Enterprise-grade infrastructure with security, scalability, and monitoring

terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }

  backend "gcs" {
    bucket = "retail-analytics-v3-terraform-state"
    prefix = "terraform/state"
  }
}

# Random suffix for unique resource names
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# ============================================================================
# GOOGLE CLOUD PLATFORM RESOURCES
# ============================================================================

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# BigQuery Datasets for Retail Analytics
resource "google_bigquery_dataset" "retail_analytics_v3" {
  dataset_id    = "retail_analytics_v3_${random_string.suffix.result}"
  friendly_name = "Retail Analytics v3.0"
  description   = "Enhanced retail analytics with multimodal AI processing"
  location      = var.gcp_region

  labels = {
    environment = var.environment
    project     = "retail-analytics-v3"
    managed_by  = "terraform"
  }
}

resource "google_bigquery_dataset" "retail_models_v3" {
  dataset_id    = "retail_models_v3_${random_string.suffix.result}"
  friendly_name = "AI Models Storage v3.0"
  description   = "Storage for AI models, embeddings, and training data"
  location      = var.gcp_region

  labels = {
    environment = var.environment
    project     = "retail-analytics-v3"
    managed_by  = "terraform"
  }
}

resource "google_bigquery_dataset" "retail_insights_v3" {
  dataset_id    = "retail_insights_v3_${random_string.suffix.result}"
  friendly_name = "Business Insights v3.0"
  description   = "Generated business insights and analytics results"
  location      = var.gcp_region

  labels = {
    environment = var.environment
    project     = "retail-analytics-v3"
    managed_by  = "terraform"
  }
}

# Cloud Storage Buckets
resource "google_storage_bucket" "retail_data_v3" {
  name          = "retail-analytics-v3-data-${random_string.suffix.result}"
  location      = var.gcp_region
  storage_class = "STANDARD"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  labels = {
    environment = var.environment
    project     = "retail-analytics-v3"
    managed_by  = "terraform"
  }
}

resource "google_storage_bucket" "retail_models_v3" {
  name          = "retail-analytics-v3-models-${random_string.suffix.result}"
  location      = var.gcp_region
  storage_class = "STANDARD"

  versioning {
    enabled = true
  }

  labels = {
    environment = var.environment
    project     = "retail-analytics-v3"
    managed_by  = "terraform"
  }
}

# Vertex AI Connection for BigQuery ML
resource "google_bigquery_connection" "vertex_ai" {
  connection_id = "vertex_ai_connection_${random_string.suffix.result}"
  location      = var.gcp_region
  friendly_name = "Vertex AI Connection for Retail Analytics"
  description   = "Connection to Vertex AI for advanced ML capabilities"

  cloud_resource {}
}

# IAM Service Account for BigQuery
resource "google_service_account" "bigquery_sa" {
  account_id   = "retail-analytics-sa-${random_string.suffix.result}"
  display_name = "Retail Analytics Service Account"
  description  = "Service account for BigQuery and AI operations"
}

# IAM Roles for Service Account
resource "google_project_iam_member" "bigquery_admin" {
  project = var.gcp_project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.bigquery_sa.email}"
}

resource "google_project_iam_member" "vertex_ai_user" {
  project = var.gcp_project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.bigquery_sa.email}"
}

resource "google_project_iam_member" "storage_admin" {
  project = var.gcp_project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.bigquery_sa.email}"
}

# ============================================================================
# AWS RESOURCES (Optional - for hybrid deployment)
# ============================================================================

provider "aws" {
  region = var.aws_region
}

# VPC for Application Deployment
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "retail-analytics-v3-${var.environment}"
    Environment = var.environment
    Project     = "retail-analytics-v3"
    ManagedBy   = "terraform"
  }
}

# Subnets
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name        = "retail-analytics-v3-public-${count.index + 1}"
    Environment = var.environment
    Type        = "public"
  }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name        = "retail-analytics-v3-private-${count.index + 1}"
    Environment = var.environment
    Type        = "private"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "retail-analytics-v3-igw"
    Environment = var.environment
  }
}

# NAT Gateway for private subnets
resource "aws_eip" "nat" {
  count = 2
  vpc   = true

  tags = {
    Name        = "retail-analytics-v3-nat-eip-${count.index + 1}"
    Environment = var.environment
  }
}

resource "aws_nat_gateway" "main" {
  count         = 2
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = {
    Name        = "retail-analytics-v3-nat-${count.index + 1}"
    Environment = var.environment
  }
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name        = "retail-analytics-v3-public-rt"
    Environment = var.environment
  }
}

resource "aws_route_table" "private" {
  count  = 2
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = {
    Name        = "retail-analytics-v3-private-rt-${count.index + 1}"
    Environment = var.environment
  }
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# Security Groups
resource "aws_security_group" "alb" {
  name_prefix = "retail-analytics-v3-alb-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "retail-analytics-v3-alb-sg"
    Environment = var.environment
  }
}

resource "aws_security_group" "app" {
  name_prefix = "retail-analytics-v3-app-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "retail-analytics-v3-app-sg"
    Environment = var.environment
  }
}

resource "aws_security_group" "database" {
  name_prefix = "retail-analytics-v3-db-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  tags = {
    Name        = "retail-analytics-v3-db-sg"
    Environment = var.environment
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "retail-analytics-v3-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = aws_subnet.public[*].id

  enable_deletion_protection = var.environment == "production"

  tags = {
    Name        = "retail-analytics-v3-alb"
    Environment = var.environment
  }
}

# ALB Target Group
resource "aws_lb_target_group" "app" {
  name_prefix = "retail-"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id

  health_check {
    path                = "/health"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = {
    Name        = "retail-analytics-v3-tg"
    Environment = var.environment
  }
}

# ALB Listener
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# RDS PostgreSQL Database
resource "aws_db_instance" "postgres" {
  identifier             = "retail-analytics-v3-${var.environment}"
  engine                 = "postgres"
  engine_version         = "15.4"
  instance_class         = var.db_instance_class
  allocated_storage      = 20
  storage_type           = "gp2"
  db_name                = "retail_analytics"
  username               = var.db_username
  password               = var.db_password
  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  multi_az               = var.environment == "production"
  backup_retention_period = 7
  skip_final_snapshot    = var.environment != "production"

  tags = {
    Name        = "retail-analytics-v3-db"
    Environment = var.environment
  }
}

resource "aws_db_subnet_group" "main" {
  name       = "retail-analytics-v3-${var.environment}"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name        = "retail-analytics-v3-db-subnet-group"
    Environment = var.environment
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "retail-analytics-v3-${var.environment}"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]

  tags = {
    Name        = "retail-analytics-v3-redis"
    Environment = var.environment
  }
}

resource "aws_elasticache_subnet_group" "main" {
  name       = "retail-analytics-v3-${var.environment}"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_security_group" "redis" {
  name_prefix = "retail-analytics-v3-redis-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  tags = {
    Name        = "retail-analytics-v3-redis-sg"
    Environment = var.environment
  }
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "retail-analytics-v3-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  tags = {
    Name        = "retail-analytics-v3-cpu-alarm"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "high_memory" {
  alarm_name          = "retail-analytics-v3-high-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "System/Linux"
  period              = "300"
  statistic           = "Average"
  threshold           = "85"
  alarm_description   = "This metric monitors memory utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  tags = {
    Name        = "retail-analytics-v3-memory-alarm"
    Environment = var.environment
  }
}

# SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {
  name = "retail-analytics-v3-alerts-${var.environment}"

  tags = {
    Name        = "retail-analytics-v3-alerts"
    Environment = var.environment
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

# Outputs
output "gcp_project_id" {
  description = "Google Cloud Project ID"
  value       = var.gcp_project_id
}

output "bigquery_datasets" {
  description = "BigQuery dataset IDs"
  value = {
    retail_analytics = google_bigquery_dataset.retail_analytics_v3.dataset_id
    retail_models    = google_bigquery_dataset.retail_models_v3.dataset_id
    retail_insights  = google_bigquery_dataset.retail_insights_v3.dataset_id
  }
}

output "storage_buckets" {
  description = "Cloud Storage bucket names"
  value = {
    data_bucket   = google_storage_bucket.retail_data_v3.name
    models_bucket = google_storage_bucket.retail_models_v3.name
  }
}

output "aws_vpc_id" {
  description = "AWS VPC ID"
  value       = aws_vpc.main.id
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = aws_lb.main.dns_name
}

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.postgres.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}