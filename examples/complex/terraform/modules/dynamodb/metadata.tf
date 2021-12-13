module "metadata" {
  source = "../resource_metadata"

  metadata = var.metadata

  instanced_resources = {
    "dynamodb"        = [var.name]
  }
}
