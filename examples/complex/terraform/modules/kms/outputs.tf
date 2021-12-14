output "arn" {
  value = {
    for key, value in aws_kms_key.this :
    (key) => value["arn"]
  }
}

output "key_id" {
  value = {
    for key, value in aws_kms_key.this :
    (key) => value["key_id"]
  }
}

output "alias_arn" {
  value = {
    for key, value in aws_kms_alias.this :
    (key) => value["arn"]
  }
}
