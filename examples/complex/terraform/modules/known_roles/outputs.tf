output "this_account" {
  value = merge(
    {
      for id, name in var.roles :
      id => "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${name}"
    },
    {
      root = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
    }
  )
}

output "all_accounts" {
  value = merge(
    {
      for id, name in var.roles :
      id => [
        for account_id in var.account_ids :
        "arn:aws:iam::${account_id}:role/${name}"
      ]
    },
    {
      root = [
        for account_id in var.account_ids :
        "arn:aws:iam::${account_id}:root"
      ]
    }
  )
}
