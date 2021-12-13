variable "metadata" {
  description = "deployment metadata"
}

variable "keys" {
  description = "KMS keys/access levels"
}

variable "tags" {
  description = "Tags applied to all keys"
  default     = {}
}

variable "deletion_window" {
  description = "Deletion window in days"
  default     = 10
}
