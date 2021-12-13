module "metadata" {
  source = "../resource_metadata"

  metadata = var.metadata

  instanced_resources = {
    aws_dynamodb_table = ["terraform"]
  }
}
