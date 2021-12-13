data "aws_caller_identity" "current" {}

data "aws_arn" "caller" {
  arn = data.aws_caller_identity.current.arn
}

locals {
  account_id = data.aws_caller_identity.current.account_id

  # resolve the root user arn
  root_arn = "arn:aws:iam::${local.account_id}:root"

  # this ugliness resolves the caller ARN - in the case of an assumed role, it resolves to the role that was assumed.
  # is there a cleaner way?
  caller_arn = data.aws_arn.caller.service == "sts" && element(split("/", data.aws_arn.caller.resource), 0) == "assumed-role" ? "arn:${data.aws_arn.caller.partition}:iam::${data.aws_arn.caller.account}:${join("/", slice(split("/", replace(data.aws_arn.caller.resource, "/^assumed-/", "")), 0, 2))}" : data.aws_caller_identity.current.arn

  whitelisted_arns = [local.root_arn, local.caller_arn]

  arn_aliases = {
    root        = local.root_arn
    self        = local.caller_arn
    caller      = local.caller_arn
    autoscaling = "arn:aws:iam::${local.account_id}:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling"
  }

  # resolve ARN aliases
  policies = { for policy_name, policy in var.policies :
    policy_name => {
      resources = policy["resources"]
      principals = { for action_set, principals in policy["principals"] :
        (action_set) => [for arn in principals :
          lookup(local.arn_aliases, arn, arn)
        ]
      }
    }
  }

  policy_root_arns = {
    for policy_name, policy in local.policies :
    policy_name => {
      for action_set, principals in policy["principals"] :
      action_set => distinct([
        for arn in principals :
        "arn:aws:iam::${element(split(":", arn), 4)}:root"
      ])
    }
  }

}

data "aws_iam_policy_document" "this" {
  for_each = local.policies

  # allow permissions
  dynamic "statement" {
    for_each = {
      for action_set, principals in each.value["principals"] :
      action_set => principals if principals != []
    }
    iterator = statement

    content {
      sid       = "allow_${statement.key}"
      effect    = "Allow"
      resources = each.value["resources"]
      actions   = var.actions[statement.key]

      principals {
        type        = "AWS"
        identifiers = setunion(local.policy_root_arns[each.key][statement.key], setunion(statement.value))
      }

      condition {
        # if any principals end in :root then use StringLike, otherwise StringEquals
        test     = length([for arn in setunion(statement.value) : arn if trimsuffix(arn, ":root") != arn]) > 0 ? "StringLike" : "StringEquals"
        variable = "aws:PrincipalArn"
        # now replace any suffixes ending in :root with :*
        values = [for arn in setunion(statement.value) : replace(arn, "/:root$/", ":*")]
      }

    }

  }

  dynamic "statement" {
    for_each = var.explicit_deny == true ? each.value["principals"] : {}
    iterator = statement

    content {
      sid       = "deny_${statement.key}"
      effect    = "Deny"
      resources = each.value["resources"]
      actions   = var.actions[statement.key]

      principals {
        type        = "*"
        identifiers = ["*"]
      }

      condition {
        test     = length([for arn in setunion(statement.value) : arn if trimsuffix(arn, ":root") != arn]) > 0 ? "StringNotLike" : "StringNotEquals"
        variable = "aws:PrincipalArn"
        values   = [for arn in setunion(statement.value) : replace(arn, "/:root$/", ":*")]
      }
    }
  }

  dynamic "statement" {
    for_each = var.explicit_deny == true ? { deny : true } : {}

    content {
      sid       = "explicit_deny"
      effect    = "Deny"
      resources = each.value["resources"]

      principals {
        type        = "*"
        identifiers = ["*"]
      }

      not_actions = distinct(flatten(values(var.actions)))

      condition {
        test     = "StringNotEquals"
        variable = "aws:PrincipalArn"
        values   = local.whitelisted_arns
      }
    }
  }
}
