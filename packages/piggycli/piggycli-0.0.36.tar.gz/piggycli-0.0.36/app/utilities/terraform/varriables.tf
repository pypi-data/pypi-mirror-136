variable "region" {
  type        = string
  description = "AWS Region"
}

variable "aws_access_key_id" {
  type        = string
  description = "AWS Access Key ID"
}

variable "aws_secret_access_key" {
  type        = string
  description = "AWS Secret Access Key"
}

variable "private_subnets" {
  type    = list(string)
  default = ["10.0.1.0/28", "10.0.2.0/28", "10.0.3.0/28"]
}

variable "ssh_key_name" {
  type        = string
  description = "name of the SSH used to connect to EC2 Instance"
}

variable "allowed_ips" {
  type        = list(string)
  description = "IP Address allowed to connect to EC2 Instance"
  default     = ["67.85.179.67/32"]
}
