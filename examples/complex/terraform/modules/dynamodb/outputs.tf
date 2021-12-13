output "arn" {
  description = "Redis Primary Endpoint"
  value       = aws_dynamodb_table.this.arn
}

output "id" {
  description = "Redis Primary Endpoint"
  value       = aws_dynamodb_table.this.id
}
