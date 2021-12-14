output "id" {
  description = "The URL of the queue."
  value       = aws_sqs_queue.this.id
}

output "arn" {
  description = "The Amazon Resource Name (ARN) of the queue."
  value       = aws_sqs_queue.this.arn
}

output "name" {
  description = "Name of the SQS queue"
  value       = aws_sqs_queue.this.name
}
