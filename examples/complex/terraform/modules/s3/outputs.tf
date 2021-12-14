output "id" {
  description = "ID of created buckets"
  value = aws_s3_bucket.this.id
}

output "arn" {
  description = "ARN of created buckets"
  value =  aws_s3_bucket.this.arn
  
}
