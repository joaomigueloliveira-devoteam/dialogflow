variable "project_id" {
  type        = string
  description = "ID of the project."
}

variable "artifact_registry_repository_id" {
  type        = string
  description = "The last part of the repository name."
}

variable "artifact_registry_format" {
  type        = string
  description = "The format of packages that are stored in the repository."
  default     = "DOCKER"
}

variable "artifact_registry_location" {
  type        = string
  description = "Location of the bucket created by this terraform module. You can select a region, dual-region, or multi-region."
}

variable "artifact_registry_description" {
  type        = string
  description = "(Optional) Description of the Artifact Registry."
  default     = null
}

variable "artifact_registry_role_group_map" {
  type        = map(list(string))
  description = "A map with each role as key and lists of members or groups as values."
  default     = {}
}
