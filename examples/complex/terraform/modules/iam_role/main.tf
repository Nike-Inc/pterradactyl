data "aws_iam_policy_document" "assume_role_policy" {
  dynamic "statement" {
    for_each = length(local.allowed_services) > 0 ? [true] : []

    content {
      actions = ["sts:AssumeRole"]

      principals {
        type        = "Service"
        identifiers = local.allowed_services
      }
    }
  }

  dynamic "statement" {
    for_each = length(var.allowed_roles) > 0 ? [true] : []

    content {
      actions = ["sts:AssumeRole", "sts:TagSession"]

      principals {
        type        = "AWS"
        identifiers = var.allowed_roles
      }
    }
  }

  dynamic "statement" {
    for_each = toset(var.external_roles)

    content {
      actions = ["sts:AssumeRole"]

      principals {
        type        = "AWS"
        identifiers = statement.value["account_id"]
      }

      condition {
        test     = "StringEquals"
        values   = statement.value["external_id"]
        variable = "sts:ExternalId"
      }
    }
  }

  dynamic "statement" {
    for_each = toset(var.wildcard_roles)

    content {
      actions = ["sts:AssumeRole"]

      principals {
        type        = "AWS"
        identifiers = statement.value["account_id"]
      }
      condition {
        test     = "StringLike"
        values   = statement.value["role_arn"]
        variable = "aws:PrincipalArn"
      }
    }
  }
}

resource "aws_iam_role" "this" {
  name = module.metadata.names.aws_iam_role[var.name]

  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
  tags = module.metadata.tags.aws_iam_role[var.name]
}

resource "aws_iam_instance_profile" "this" {
  count = var.instance_profile == true ? 1 : 0

  name = module.metadata.names.aws_iam_instance_profile[var.name]
  role = aws_iam_role.this.name
}

data "aws_iam_policy_document" "this" {
  count = length(var.policy) > 0 ? 1 : 0

  dynamic "statement" {
    for_each = var.policy

    content {
      resources = statement.value["resources"]
      actions   = statement.value["actions"]
    }
  }
}

resource "aws_iam_policy" "this" {
  count = length(var.policy) > 0 ? 1 : 0

  name        = module.metadata.names.aws_iam_policy[var.name]
  path        = module.metadata.paths.aws_iam_policy[var.name]
  description = "Service account policy: ${var.name}"
  policy      = data.aws_iam_policy_document.this.0.json
}

resource "aws_iam_role_policy_attachment" "this" {
  count = length(var.policy) > 0 ? 1 : 0

  role       = aws_iam_role.this.name
  policy_arn = aws_iam_policy.this.0.arn
}

resource "aws_iam_role_policy_attachment" "policy_attachment" {
  for_each = local.policy_attachments

  role       = aws_iam_role.this.name
  policy_arn = each.value
}
