module "kms_least_privilege" {
  source = "../../modules/least_privilege"

  actions = {
    admin = [
      "kms:*KeyPolicy",
      "kms:*KeyRotationStatus",
      "kms:*ResourceTags",
      "kms:TagResource",
      "kms:UntagResource",
      "kms:*Alias",
      "kms:ScheduleKeyDeletion",
      "kms:EnableKeyRotation",
      "kms:UpdateKeyDescription",
      "kms:ListGrants"
    ]

    common = [
      "kms:DescribeKey"
    ]

    encrypt = [
      "kms:Encrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*"
    ]

    decrypt = [
      "kms:Decrypt"
    ]

    grant = [
      "kms:CreateGrant"
    ]
  }

  policies = {
    for key, policies in var.keys :
    (key) => {
      resources = ["*"]
      principals = {
        admin = ["self"]

        encrypt = setunion(lookup(policies, "encrypt", []), lookup(policies, "encrypt_decrypt", []))
        decrypt = setunion(lookup(policies, "decrypt", []), lookup(policies, "encrypt_decrypt", []))
        grant   = lookup(policies, "grant", [])

        common = setunion(["self"], flatten([
          for action_set, principals in policies :
          principals
        ]))

      }
    }
  }
}

resource "aws_kms_key" "this" {
  for_each = var.keys

  description             = lookup(each.value, "description", null)
  deletion_window_in_days = var.deletion_window
  enable_key_rotation     = true
  policy                  = module.kms_least_privilege.policies[each.key]
  tags                    = module.metadata.tags.aws_kms_key[each.key]
}

resource "aws_kms_alias" "this" {
  for_each      = var.keys
  name          = "alias/${module.metadata.names.aws_kms_key_alias[each.key]}"
  target_key_id = aws_kms_key.this[each.key].id
}
