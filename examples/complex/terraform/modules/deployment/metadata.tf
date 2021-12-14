module "metadata" {
  source = "../resource_metadata"

  metadata = local.metadata

  singleton_resources = ["deployment_id"]

}
