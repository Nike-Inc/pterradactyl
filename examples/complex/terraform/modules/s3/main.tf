
resource "aws_s3_bucket" "this" {
  bucket = var.name
  acl    = "private"
  tags   = module.metadata.tags.s3[var.name] 
}