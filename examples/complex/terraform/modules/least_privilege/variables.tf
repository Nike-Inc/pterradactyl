variable "actions" {
  description = "Map of action sets"
  type        = map(list(string))
}

variable "policies" {
  description = "Map of policies"
  type = map(object({
    resources  = list(string)
    principals = map(list(string))
  }))
}

variable "explicit_deny" {
  description = "Generate an explicit default deny policy"
  default     = false
}
