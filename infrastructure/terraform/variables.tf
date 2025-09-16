# ============================================================================
# Intelligent Retail Analytics Engine v3.0 - Terraform Variables
# Enterprise-grade infrastructure configuration
# ============================================================================

# ============================================================================
# ENVIRONMENT SETTINGS
# ============================================================================

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "development"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production"
  }
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "retail-analytics-v3"
}

# ============================================================================
# GOOGLE CLOUD PLATFORM SETTINGS
# ============================================================================

variable "gcp_project_id" {
  description = "Google Cloud Project ID"
  type        = string
  sensitive   = true

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.gcp_project_id))
    error_message = "GCP Project ID must be valid format"
  }
}

variable "gcp_region" {
  description = "Google Cloud region"
  type        = string
  default     = "us-central1"

  validation {
    condition = contains([
      "us-central1", "us-east1", "us-west1", "us-west2",
      "europe-west1", "europe-west2", "asia-east1", "asia-southeast1"
    ], var.gcp_region)
    error_message = "GCP region must be a valid Google Cloud region"
  }
}

variable "gcp_zone" {
  description = "Google Cloud zone"
  type        = string
  default     = "us-central1-a"
}

# ============================================================================
# AWS SETTINGS
# ============================================================================

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"

  validation {
    condition = contains([
      "us-east-1", "us-east-2", "us-west-1", "us-west-2",
      "eu-west-1", "eu-central-1", "ap-southeast-1", "ap-southeast-2"
    ], var.aws_region)
    error_message = "AWS region must be a valid AWS region"
  }
}

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"

  validation {
    condition = contains([
      "db.t3.micro", "db.t3.small", "db.t3.medium",
      "db.t4g.micro", "db.t4g.small", "db.t4g.medium",
      "db.r6g.large", "db.r6g.xlarge"
    ], var.db_instance_class)
    error_message = "Database instance class must be a valid RDS instance type"
  }
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "retail_admin"
  sensitive   = true

  validation {
    condition     = length(var.db_username) >= 3 && length(var.db_username) <= 16
    error_message = "Database username must be between 3 and 16 characters"
  }
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.db_password) >= 8
    error_message = "Database password must be at least 8 characters"
  }
}

variable "db_allocated_storage" {
  description = "Database allocated storage in GB"
  type        = number
  default     = 20

  validation {
    condition     = var.db_allocated_storage >= 20 && var.db_allocated_storage <= 65536
    error_message = "Database storage must be between 20GB and 65536GB"
  }
}

variable "db_backup_retention_period" {
  description = "Database backup retention period in days"
  type        = number
  default     = 7

  validation {
    condition     = var.db_backup_retention_period >= 0 && var.db_backup_retention_period <= 35
    error_message = "Backup retention period must be between 0 and 35 days"
  }
}

# ============================================================================
# NETWORKING CONFIGURATION
# ============================================================================

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid CIDR block"
  }
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]

  validation {
    condition = alltrue([
      for cidr in var.public_subnet_cidrs : can(cidrhost(cidr, 0))
    ])
    error_message = "All public subnet CIDRs must be valid"
  }
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]

  validation {
    condition = alltrue([
      for cidr in var.private_subnet_cidrs : can(cidrhost(cidr, 0))
    ])
    error_message = "All private subnet CIDRs must be valid"
  }
}

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

variable "app_port" {
  description = "Application port"
  type        = number
  default     = 8000

  validation {
    condition     = var.app_port >= 1024 && var.app_port <= 65535
    error_message = "Application port must be between 1024 and 65535"
  }
}

variable "health_check_path" {
  description = "Health check path"
  type        = string
  default     = "/health"
}

variable "app_image" {
  description = "Docker image for the application"
  type        = string
  default     = "retail-analytics-v3:latest"
}

# ============================================================================
# CACHE CONFIGURATION
# ============================================================================

variable "redis_node_type" {
  description = "Redis node type"
  type        = string
  default     = "cache.t3.micro"

  validation {
    condition = contains([
      "cache.t3.micro", "cache.t3.small", "cache.t3.medium",
      "cache.t4g.micro", "cache.t4g.small", "cache.t4g.medium",
      "cache.r6g.large", "cache.r6g.xlarge"
    ], var.redis_node_type)
    error_message = "Redis node type must be a valid ElastiCache instance type"
  }
}

variable "redis_num_cache_nodes" {
  description = "Number of Redis cache nodes"
  type        = number
  default     = 1

  validation {
    condition     = var.redis_num_cache_nodes >= 1 && var.redis_num_cache_nodes <= 6
    error_message = "Redis cache nodes must be between 1 and 6"
  }
}

# ============================================================================
# MONITORING & ALERTING
# ============================================================================

variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "enable_alerts" {
  description = "Enable SNS alerts"
  type        = bool
  default     = true
}

variable "cpu_threshold" {
  description = "CPU utilization threshold for alerts"
  type        = number
  default     = 80

  validation {
    condition     = var.cpu_threshold >= 0 && var.cpu_threshold <= 100
    error_message = "CPU threshold must be between 0 and 100"
  }
}

variable "memory_threshold" {
  description = "Memory utilization threshold for alerts"
  type        = number
  default     = 85

  validation {
    condition     = var.memory_threshold >= 0 && var.memory_threshold <= 100
    error_message = "Memory threshold must be between 0 and 100"
  }
}

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

variable "enable_deletion_protection" {
  description = "Enable deletion protection for critical resources"
  type        = bool
  default     = false
}

variable "enable_encryption" {
  description = "Enable encryption for data at rest"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "kms_key_rotation" {
  description = "Enable KMS key rotation"
  type        = bool
  default     = true
}

# ============================================================================
# COST OPTIMIZATION
# ============================================================================

variable "enable_cost_allocation_tags" {
  description = "Enable cost allocation tags"
  type        = bool
  default     = true
}

variable "budget_limit" {
  description = "Monthly budget limit in USD"
  type        = number
  default     = 500

  validation {
    condition     = var.budget_limit > 0
    error_message = "Budget limit must be greater than 0"
  }
}

variable "budget_alert_threshold" {
  description = "Budget alert threshold percentage"
  type        = number
  default     = 80

  validation {
    condition     = var.budget_alert_threshold >= 0 && var.budget_alert_threshold <= 100
    error_message = "Budget alert threshold must be between 0 and 100"
  }
}

# ============================================================================
# TAGS
# ============================================================================

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "retail-analytics-v3"
    ManagedBy   = "terraform"
    Owner       = "data-engineering-team"
    CostCenter  = "analytics"
  }
}

variable "environment_tags" {
  description = "Environment-specific tags"
  type        = map(string)
  default = {}
}

# ============================================================================
# ADVANCED FEATURES
# ============================================================================

variable "enable_vertex_ai" {
  description = "Enable Vertex AI integration"
  type        = bool
  default     = true
}

variable "enable_bigquery_ml" {
  description = "Enable BigQuery ML features"
  type        = bool
  default     = true
}

variable "enable_cloud_run" {
  description = "Enable Cloud Run for serverless deployment"
  type        = bool
  default     = false
}

variable "enable_api_gateway" {
  description = "Enable API Gateway for advanced routing"
  type        = bool
  default     = false
}

# ============================================================================
# COMPLIANCE & GOVERNANCE
# ============================================================================

variable "data_classification" {
  description = "Data classification level"
  type        = string
  default     = "internal"

  validation {
    condition     = contains(["public", "internal", "confidential", "restricted"], var.data_classification)
    error_message = "Data classification must be one of: public, internal, confidential, restricted"
  }
}

variable "compliance_frameworks" {
  description = "Compliance frameworks to adhere to"
  type        = list(string)
  default     = ["gdpr", "soc2"]

  validation {
    condition = alltrue([
      for framework in var.compliance_frameworks : contains([
        "gdpr", "hipaa", "pci-dss", "soc2", "iso27001", "ccpa"
      ], framework)
    ])
    error_message = "Compliance frameworks must be valid"
  }
}

# ============================================================================
# SCALING CONFIGURATION
# ============================================================================

variable "min_instances" {
  description = "Minimum number of application instances"
  type        = number
  default     = 1

  validation {
    condition     = var.min_instances >= 1
    error_message = "Minimum instances must be at least 1"
  }
}

variable "max_instances" {
  description = "Maximum number of application instances"
  type        = number
  default     = 5

  validation {
    condition     = var.max_instances >= var.min_instances
    error_message = "Maximum instances must be greater than or equal to minimum instances"
  }
}

variable "target_cpu_utilization" {
  description = "Target CPU utilization for auto-scaling"
  type        = number
  default     = 70

  validation {
    condition     = var.target_cpu_utilization >= 10 && var.target_cpu_utilization <= 90
    error_message = "Target CPU utilization must be between 10 and 90"
  }
}

variable "scale_in_cooldown" {
  description = "Cooldown period for scaling in (seconds)"
  type        = number
  default     = 300

  validation {
    condition     = var.scale_in_cooldown >= 60
    error_message = "Scale in cooldown must be at least 60 seconds"
  }
}

variable "scale_out_cooldown" {
  description = "Cooldown period for scaling out (seconds)"
  type        = number
  default     = 60

  validation {
    condition     = var.scale_out_cooldown >= 60
    error_message = "Scale out cooldown must be at least 60 seconds"
  }
}