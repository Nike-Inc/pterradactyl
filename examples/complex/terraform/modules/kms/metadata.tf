module "metadata" {
  source = "../resource_metadata"

  metadata = var.metadata
  tags     = var.tags

  instanced_resources = {
    aws_kms_key       = keys(var.keys)
    aws_kms_key_alias = keys(var.keys)
  }
}
