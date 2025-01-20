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