variable "aws_account" {
  type        = string
  description = "AWS account name"
}

variable "db_name" {
  type        = string
  description = "RDS database name"
}

variable "db_username" {
  type        = string
  description = "RDS database username"
}

variable "db_password" {
  type        = string
  description = "RDS database password"
  sensitive   = true
}

variable "vpc_arn" {
  type        = string
  description = "VPC ARN for all resources"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for the database"
}

variable "security_group_id" {
  type        = string
  description = "Security group ID for the database"
}
