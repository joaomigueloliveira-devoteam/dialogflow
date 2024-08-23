resource "google_artifact_registry_repository" "repository" {
  project       = var.project_id
  format        = var.artifact_registry_format
  repository_id = var.artifact_registry_repository_id
  location      = var.artifact_registry_location
  description   = var.artifact_registry_description
}
