variable "metadata" {
  description = "metadata"
  type = object({
    account_alias  = string
    account_family = string
    account_type   = string
    product        = string
    n              = number
    region         = string
    azs            = list(string)
    tags           = map(string)
    deployment     = string
  })
}

variable "tags" {
  description = "Tags applied to all resources"
  default     = {}
}

variable "resource_tags" {
  description = "Tags applied to resources of specific types"
  type        = map(map(string))
  default     = {}
}

variable "singleton_resources" {
  description = "Resources with a single instance"
  type        = list(string)
  default     = []
}

variable "instanced_resources" {
  description = "Resources with multiple named instances"
  type        = map(list(string))
  default     = {}
}

variable "zonal_resources" {
  description = "Resources with a single instance per zone"
  type        = list(string)
  default     = []
}

variable "instanced_zonal_resources" {
  description = "Resources with multiple named instances per zone"
  type        = map(list(string))
  default     = {}
}

variable "geo_resources" {
  description = "Geographically-scoped resources (e.g. storage buckets)"
  type        = map(map(list(string)))
  default     = {}
}
