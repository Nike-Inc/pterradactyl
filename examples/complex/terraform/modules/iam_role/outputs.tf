output "arn" {
  value = aws_iam_role.this.arn
}

output "instance_profile_name" {
  value = var.instance_profile == true ? element(aws_iam_instance_profile.this.*.name, 0) : null
}
