output "tags" {
  description = "Structured map of tags for requested resources"
  value       = local.tags
}

output "names" {
  description = "Structured map of names for requested resources"
  value       = local.names
}

output "paths" {
  description = "Structured map of paths for requested resources"
  value       = local.paths
}
