resource "aws_sns_topic" "sns_topic" {
  name = "ab-logger-sns"
}


resource "aws_db_instance" "db_instance" {
  identifier        = "ab-logger-db"
  engine            = "mysql"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  username          = var.db_username
  password          = var.db_password
  db_name           = var.db_name
  skip_final_snapshot = true

  vpc_security_group_ids = [var.security_group_id]
  db_subnet_group_name   = aws_db_subnet_group.db_subnet_group.name

}

resource "aws_db_subnet_group" "db_subnet_group" {
  name        = "ab-logger-db-subnet-group"
  description = "Subnet group for RDS instance"
  subnet_ids  = var.subnet_ids
}

resource "aws_iam_role" "lambda_role" {
  name = "ab-logger-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name = "ab-logger-lambda-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

data "archive_file" "lambda_zip" {
   type        = "zip"
   source_dir = "../lambda-resources"
   output_path = "ab-logger-lambda-resources.zip"
 }

resource "aws_lambda_function" "lambda_function" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "ab-logger-lambda"
  handler          = "ab-logger-lambda.handler" 
  runtime          = "python3.10" 
  role             = aws_iam_role.lambda_role.arn
  source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)

  environment {
    variables = {
      DB_HOST     = aws_db_instance.db_instance.address
      DB_USERNAME = var.db_username
      DB_PASSWORD = var.db_password
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [var.security_group_id]
  }
  timeout = 5

}

resource "aws_sns_topic_subscription" "sns_subscription" {
  topic_arn = aws_sns_topic.sns_topic.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.lambda_function.arn
}

resource "aws_lambda_permission" "sns_lambda_permission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.sns_topic.arn
}

# # Security group for RDS (optional, for tighter control)
# resource "aws_security_group" "rds_security_group" {
#   name        = "rds-security-group"
#   description = "Allow MySQL access"
#   ingress {
#     from_port   = 3306
#     to_port     = 3306
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]  # Adjust for better security
#   }
# }

# # Secrets Manager (optional) to securely store the RDS password
# resource "aws_secretsmanager_secret" "db_password_secret" {
#   name        = "rds-db-password"
#   description = "RDS DB password for Lambda"
# }

# resource "aws_secretsmanager_secret_version" "db_password_version" {
#   secret_id     = aws_secretsmanager_secret.db_password_secret.id
#   secret_string = jsonencode({ password = "admin123" })
# }

output "sns_topic_arn" {
  value = aws_sns_topic.sns_topic.arn
}

output "rds_instance_endpoint" {
  value = aws_db_instance.db_instance.address
}
