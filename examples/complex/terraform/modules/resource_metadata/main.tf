locals {

  # tags applied to all resources
  base_tags = merge(var.metadata.tags, var.tags)

  # naming logic

  singleton_names = {
    for type in var.singleton_resources :
    type => local.singleton_name
  }

  instanced_names = {
    for type, resources in var.instanced_resources :
    type => {
      for resource in resources :
      resource => format(local.instanced_name_format, replace(lower(resource), local.strip_chars, ""))
    }
  }

  geo_names = {
    for type, geos in var.geo_resources :
    type => {
      for geo, resources in geos :
      geo => {
        for resource in resources :
        resource => format(local.geo_name_format, geo, replace(lower(resource), local.strip_chars, ""))
      }
    }
  }

  zonal_names = {
    for type in var.zonal_resources :
    type => {
      for az in var.metadata.azs :
      az => format(local.zonal_name_format, local.az_code[az])
    }
  }

  instanced_zonal_names = {
    for type, resources in var.instanced_zonal_resources :
    type => {
      for resource in resources :
      resource => {
        for az in var.metadata.azs :
        az => format(local.instanced_zonal_name_format,
          local.az_code[az],
          replace(lower(resource), local.strip_chars, "")
        )
      }
    }
  }

  # tagging logic
  singleton_tags = {
    for type, name in local.singleton_names :
    type => merge(
      local.base_tags,
      lookup(var.resource_tags, type, {}),
      {
        Name                           = name,
        "resource-classifier" = local.deployment_id
      }
    )
  }

  instanced_tags = {
    for type, resources in local.instanced_names :
    type => {
      for resource, name in resources :
      resource => merge(
        local.base_tags,
        lookup(var.resource_tags, type, {}),
        {
          Name                                       = name,
          "resource-classifier/${resource}" = local.deployment_id
        }
      )
    }
  }

  geo_tags = {
    for type, geos in local.geo_names :
    type => {
      for geo, resources in geos :
      geo => {
        for resource, name in resources :
        resource => merge(
          local.base_tags,
          lookup(var.resource_tags, type, {}),
          {
            Name                                       = name,
            "resource-classifier/${resource}" = local.deployment_id
          }
        )
      }
    }
  }

  zonal_tags = {
    for type, azs in local.zonal_names :
    type => {
      for az, name in azs :
      az => merge(
        local.base_tags,
        lookup(var.resource_tags, type, {}),
        {
          Name                                   = name,
          "resource-classifier/${type}" = local.deployment_id
        }
      )
    }
  }

  instanced_zonal_tags = {
    for type, resources in local.instanced_zonal_names :
    type => {
      for resource, azs in resources :
      resource => {
        for az, name in azs :
        az => merge(
          local.base_tags,
          lookup(var.resource_tags, type, {}),
          {
            Name                                       = name,
            "resource-classifier/${resource}" = local.deployment_id
          }
        )
      }
    }
  }

  # placeholder for path logic

  singleton_paths = {
    for type in var.singleton_resources :
    type => "/"
  }

  instanced_paths = {
    for type, resources in var.instanced_resources :
    type => {
      for resource in resources :
      # hyphens are stripped from resource names
      resource => "/"
    }
  }

  geo_paths = {
    for type, geos in var.geo_resources :
    type => {
      for geo, resources in geos :
      geo => {
        for resource in resources :
        resource => "/"
      }
    }
  }

  zonal_paths = {
    for type, azs in var.zonal_resources :
    type => {
      for az in var.metadata.azs :
      az => "/"
    }
  }

  instanced_zonal_paths = {
    for type, resources in var.instanced_zonal_resources :
    type => {
      for resource in resources :
      resource => {
        for az in var.metadata.azs :
        az => "/"
      }
    }
  }

  names = merge(
    local.singleton_names,
    local.instanced_names,
    local.geo_names,
    local.zonal_names,
    local.instanced_zonal_names,
  )

  tags = merge(
    local.singleton_tags,
    local.instanced_tags,
    local.geo_tags,
    local.zonal_tags,
    local.instanced_zonal_tags,
  )

  paths = merge(
    local.singleton_paths,
    local.instanced_paths,
    local.geo_paths,
    local.zonal_paths,
    local.instanced_zonal_paths
  )

}
