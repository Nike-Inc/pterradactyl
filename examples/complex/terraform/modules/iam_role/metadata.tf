module "metadata" {
  source = "../resource_metadata"

  metadata = var.metadata
  tags     = var.tags
  instanced_resources = {
    aws_iam_role             = [var.name]
    aws_iam_instance_profile = [var.name]
    aws_iam_policy           = [var.name]
  }

}
