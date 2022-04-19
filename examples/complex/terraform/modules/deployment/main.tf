data "aws_iam_account_alias" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {}
data "aws_caller_identity" "current" {}

locals {
  account_alias_arr    = split("-", local.account_alias)
  account_alias_length = length(local.account_alias_arr)
  account_alias        = data.aws_iam_account_alias.current.account_alias
  # take everything before the last - in the account alias as the family name
  # e.g. account alias aaml-aws-hackathon-2021-test -> account_family=aaml-aws-hackathon-2021 account_type=test
  # e.g. common-clct-prod  account_family=common-clct account_type=test
  account_family = lookup(var.account_families, join("-", slice(local.account_alias_arr, 0, local.account_alias_length - 1)), var.account_families["_default_"])

  account_type = element(local.account_alias_arr, local.account_alias_length - 1)

  metadata = {
    account_alias       = local.account_alias
    account_family      = local.account_family
    account_type        = local.account_type
    account_id          = data.aws_caller_identity.current.account_id
    product             = var.product
    n                   = var.n
    region              = data.aws_region.current.name
    azs                 = data.aws_availability_zones.available.names
    tags                = merge(var.tags, local.nike_tags)
    deployment          = var.id
    account_family_code = var.account_family_code
    account_type_code   = var.account_type_code
  }
}
