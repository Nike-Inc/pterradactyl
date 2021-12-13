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
