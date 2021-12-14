data "aws_caller_identity" "this" {}

data "aws_iam_policy_document" "sqs_policy" {
  statement {
    actions = [
      "sqs:SendMessage",
      "sqs:ReceiveMessage"
    ]

    principals {
      type        = "Service"
      identifiers = ["eks.amazonaws.com"]
    }
  }
  statement {
    actions = [
      "SQS:SendMessage",
      "SQS:ReceiveMessage"
    ]

    resources = [
      "*",
    ]

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"

      values = [data.aws_caller_identity.this.account_id]
    }
  }
}


resource "aws_sqs_queue" "this" {
  name                              = var.name
  visibility_timeout_seconds        = var.visibility_timeout_seconds
  message_retention_seconds         = var.visibility_timeout_seconds
  max_message_size                  = var.max_message_size
  delay_seconds                     = var.delay_seconds
  receive_wait_time_seconds         = var.receive_wait_time_seconds
  policy                            = data.aws_iam_policy_document.sqs_policy.json
  content_based_deduplication       = var.content_based_deduplication
  kms_master_key_id                 = var.kms_master_key_id
  kms_data_key_reuse_period_seconds = var.kms_data_key_reuse_period_seconds
  tags                              = module.metadata.tags.sqs[var.name] 
}
