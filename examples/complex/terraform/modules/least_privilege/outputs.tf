output "policies" {
  description = "Generated JSON policy documents"

  value = {
    for name, policy in data.aws_iam_policy_document.this :
    (name) => policy.json
  }
}
