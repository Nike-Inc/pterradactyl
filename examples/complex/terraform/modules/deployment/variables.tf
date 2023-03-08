variable "id" {
  description = "Deployment id string"
  default     = ""
}

variable "n" {
  description = "Unique deployment ordinal"
  default     = 0
}

variable "tags" {
  description = "Custom tags applied to all resources in deployment"
  default     = {}
}

variable "product" {
  description = "Product ID"
  default     = ""
}



variable "account_families" {
  description = "Map of account alias name to family name. -IMPORTANT- Make sure to add _default_"
  /*
  example: 
  account_families = {
    "_default_" = "common"
    "projecta" = "teama"
    "projectb" = "teamb"
  }
  */
}

variable "account_family_code" {
  description = "Map of account alias name to family code. -IMPORTANT- Make sure to add common"
  /*
  example: 
  account_family_code = {
    "common" = "c"
    "projecta" = "a"
    "projectb" = "b"
  }
  */
}

variable "account_type_code" {
  description = "Map of account type to code"
  /*
  example:
  account_type_code = {
    test = "t"
    prod = "p"
  }
  */
}
