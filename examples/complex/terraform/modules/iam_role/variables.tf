variable "name" {
  description = "Role name"
}

variable "metadata" {
  description = "Deployment metadata"
}

variable "tags" {
  description = "Custom tags applied to all resources in deployment"
  default     = {}
}

variable "allowed_services" {
  description = "Services allowed to assume this role"
  type        = set(string)
  default     = []
}

variable "allowed_roles" {
  description = "Roles allowed to assume this role"
  type        = set(string)
  default     = []
}

variable "instance_profile" {
  description = "Set to true to create an ec2 instance profile"
  default     = false
}

variable "policy" {
  description = "Policy statements to associate with this role"
  default     = []
}

variable "external_roles" {
  description = "External roles allowed to assume role"
  default     = []
}

variable "wildcard_roles" {
  description = "External roles allowed to assume role"
  default     = []
}

variable "policy_attachments" {
  description = "Existing policies to attach to this role"
  default     = []
}

locals {
  allowed_services = setunion(
    var.allowed_services,
    var.instance_profile == true ? ["ec2.amazonaws.com"] : []
  )
  policy_attachments = setunion(
    var.policy_attachments,
    var.instance_profile == true ? ["arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"] : []
  )
}
