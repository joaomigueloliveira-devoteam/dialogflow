variable "project" {
  type = string
}

variable "account_id" {
  type = string
}

variable "display_name" {
  type = string
}

variable "description" {
  type = string
}

variable "disabled" {
  type = bool
}

variable "member" {
  type = string
}

variable "role" {
  type = list(string)
}
