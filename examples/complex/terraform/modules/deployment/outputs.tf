output "tags" {
  value = var.tags
}

output "metadata" {
  value = local.metadata
}

output "id" {
  description = "Deployment ID, per naming convention"
  value       = module.metadata.names.deployment_id
}
