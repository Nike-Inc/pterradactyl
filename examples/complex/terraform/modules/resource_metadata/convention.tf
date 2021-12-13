# conventions for individual components of name defined by spec
locals {

  # defined by naming convention
  account_family_code = {
    common     = "c"
    restricted = "r"
    team1      = "e"
    team2      = "v"
  }

  # defined by naming convention
  account_type_code = {
    test = "t"
    prod = "p"
  }

  # regex defining characters disallowed in name components
  strip_chars = "/[^a-z0-9]/"

  # region name with disallowed characters removed
  region_name = replace(var.metadata.region, local.strip_chars, "")

  # defined by removing the regional portion of az names
  az_code = {
    for az in var.metadata.azs :
    az => trimprefix(az, var.metadata.region)
  }

}

# formats
locals {

  # base portion of the name, applied to all resources
  base_name_format = format("%s%s-%s%d-%%s",
    local.account_family_code[var.metadata.account_family],
    local.account_type_code[var.metadata.account_type],
    var.metadata.product,
    var.metadata.n
  )

  # singleton resource names derive from base format = region
  singleton_name = format(local.base_name_format,
    local.region_name
  )

  # instanced resource names will add an instance ID at iteration time
  instanced_name_format = format("%s-%%s",
    local.singleton_name
  )

  # zonal resource names will add an AZ specifier at iteration time
  zonal_name_format = format("%s%%s",
    local.singleton_name
  )

  # instanced zonal resources additionally add an instance ID to zonal format
  instanced_zonal_name_format = format("%s-%%s",
    local.zonal_name_format
  )

  # storage buckets have a different naming convention since they're accessed globally
  geo_name_format = format("%s-%%s",
    local.base_name_format
  )

  deployment_id = local.singleton_name
}
