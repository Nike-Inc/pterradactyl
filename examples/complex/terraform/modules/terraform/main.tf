data "aws_iam_account_alias" "current" {}

variable "metadata" {
  description = "Deployment metadata"
}

locals {
  prefix = data.aws_iam_account_alias.current.account_alias
}

# basic dynamodb table resource, expand as needed but please maintain backward compatibility
resource "aws_dynamodb_table" "this" {
  name           = module.metadata.names.aws_dynamodb_table.terraform
  tags           = module.metadata.tags.aws_dynamodb_table.terraform
  billing_mode   = "PROVISIONED"
  hash_key       = "LockID"
  read_capacity  = 5
  write_capacity = 5

  attribute {
    name = "LockID"
    type = "S"
  }
}
