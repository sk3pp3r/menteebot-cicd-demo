terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
    
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

# Configure AWS Provider
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Owner       = var.owner
      Repository  = "https://github.com/sk3pp3r/menteebot-cicd-demo"
    }
  }
}

# Variables for shared configuration
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "menteebot-cicd-demo"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "owner" {
  description = "Project owner"
  type        = string
  default     = "haimc"
}

# Outputs for shared configuration
output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}

output "project_name" {
  description = "Project name"
  value       = var.project_name
}

output "environment" {
  description = "Environment name"
  value       = var.environment
} 