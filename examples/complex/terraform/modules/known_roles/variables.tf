variable "roles" {
  description = "Map of Okta role names (e.g. { admin_role = Nike.SSO.AdminRole })"
  default     = {}
}

variable "account_ids" {
  description = "List of all account IDs (for providing cross-account role ARNs)"
  default     = []
}
