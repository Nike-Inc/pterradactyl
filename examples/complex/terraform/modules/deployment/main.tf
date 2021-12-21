locals {
  account_families = {
    "_default_" = "common"
    "projecta" = "teama"
    "projectb" = "teamb"
  }
}

data "aws_iam_account_alias" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {}
data "aws_caller_identity" "current" {}

locals {
  account_alias  = data.aws_iam_account_alias.current.account_alias
  # Take everything before the last - in the account alias as the family name
  # e.g. for account alias projecta-test  account_family=projecta account_type=test
  account_family = lookup(local.account_families, element(split("-", local.account_alias), 0), local.account_families["_default_"])
  account_type   = element(split("-", local.account_alias), 2)

  metadata = {
    account_alias  = local.account_alias
    account_family = local.account_family
    account_type   = local.account_type
    account_id     = data.aws_caller_identity.current.account_id
    product        = var.product
    n              = var.n
    region         = data.aws_region.current.name
    azs            = data.aws_availability_zones.available.names
    tags           = var.tags
    deployment     = var.id
  }
}
