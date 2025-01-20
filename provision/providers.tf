terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  shared_config_files      = ["~/.aws/config"]
  shared_credentials_files = ["~/.aws/credentials"]
  profile                  = "b2b_analytics_sandbox"
}

# provider "aws" {
#   region  = "eu-central-1"
#   profile = "private"
# }