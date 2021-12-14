module "metadata" {
  source = "../resource_metadata"

  metadata = var.metadata
  tags     = var.tags
  instanced_resources = {
    "sqs"                = [var.name]
  }
}
