variable "name" {
  description = "The name of the queue to be created."
  type        = string
}

variable "visibility_timeout_seconds" {
  description = "The visibility timeout for the queue."
  type        = number
  default     = 30
}

variable "message_retention_seconds" {
  description = "The number of seconds Amazon SQS retains a message."
  type        = number
  default     = 345600
}

variable "max_message_size" {
  description = "The limit of how many bytes a message can contain before Amazon SQS rejects it."
  type        = number
  default     = 262144
}

variable "delay_seconds" {
  description = "The time in seconds that the delivery of all messages in the queue will be delayed."
  type        = number
  default     = 0
}

variable "receive_wait_time_seconds" {
  description = "The time for which a ReceiveMessage call will wait for a message to arrive (long polling) before returning."
  type        = number
  default     = 0
}

variable "fifo_queue" {
  description = "Boolean designating a FIFO queue."
  type        = bool
  default     = false
}

variable "content_based_deduplication" {
  description = "Enables content-based deduplication for FIFO queues."
  type        = bool
  default     = false
}

variable "kms_master_key_id" {
  description = "The ID of an AWS-managed customer master key (CMK) for Amazon SQS or a custom CMK."
  type        = string
  default     = null
}

variable "kms_data_key_reuse_period_seconds" {
  description = "The length of time, in seconds, for which Amazon SQS can reuse a data key to encrypt or decrypt messages before calling AWS KMS again."
  type        = number
  default     = 300
}

variable "tags" {
  description = "Tags applied to the sqs"
  default     = {}
}
