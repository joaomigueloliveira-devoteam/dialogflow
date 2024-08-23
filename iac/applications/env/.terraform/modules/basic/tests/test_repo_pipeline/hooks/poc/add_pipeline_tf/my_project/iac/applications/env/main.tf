provider "google" {
  project                     = var.project_id
  region                      = var.region
  zone                        = var.zone
  impersonate_service_account = var.service_accounts["terraform"].email
}

provider "google-beta" {
  project                     = var.project_id
  region                      = var.region
  zone                        = var.zone
  impersonate_service_account = var.service_accounts["terraform"].email
}

module "api" {
  # TODO remove after dev
  # tflint-ignore: terraform_module_pinned_source
  source = "git@github.com:devoteamgcloud/accel-vertex-ai-cookiecutter-templates.git//terraform-modules/api"

  project_id   = var.project_id
  api_services = var.api_services
}

resource "time_sleep" "api_propagation" {
  depends_on = [module.api]

  create_duration = "120s"
}

resource "google_project_iam_custom_role" "artifact_registry_role" {
  role_id     = "artifactRegistryUser"
  title       = "Artifact Registry User"
  description = "Role to be granted to dev, uat and prod projects that need access to ops AR repositories."
  permissions = [
    "artifactregistry.packages.get",
    "artifactregistry.packages.list",
    "artifactregistry.projectsettings.get",
    "artifactregistry.repositories.downloadArtifacts",
    "artifactregistry.repositories.get",
    "artifactregistry.repositories.list",
    "artifactregistry.repositories.listEffectiveTags",
    "artifactregistry.repositories.listTagBindings",
    "artifactregistry.repositories.uploadArtifacts",
    "artifactregistry.tags.get",
    "artifactregistry.tags.list",
    "artifactregistry.versions.get",
    "artifactregistry.versions.list"
  ]

  depends_on = [time_sleep.api_propagation]
}

resource "time_sleep" "role_propagation" {
  depends_on = [resource.google_project_iam_custom_role.artifact_registry_role]

  create_duration = "120s"
}

module "artifact_repository" {
  for_each = local.updated_artifact_registry_maps

  source = "git@github.com:devoteamgcloud/accel-vertex-ai-cookiecutter-templates.git//terraform-modules/artifact_registry"

  project_id = var.project_id

  artifact_registry_repository_id  = each.key
  artifact_registry_format         = each.value.format
  artifact_registry_location       = each.value.location
  artifact_registry_description    = each.value.description
  artifact_registry_role_group_map = each.value.role_group_map

  depends_on = [time_sleep.api_propagation, null_resource.dummy_pipeline_job]
}

module "buckets" {
  for_each = var.buckets

  source = "git@github.com:devoteamgcloud/tf-gcp-modules-cloud-storage.git?ref=v1.0.1"

  project_id                  = var.project_id
  name                        = each.value.name
  bucket_location             = each.value.region
  bucket_storage_class        = "STANDARD"
  bucket_force_destroy        = false
  bucket_uniform_level_access = true

  depends_on = [time_sleep.api_propagation]
}

module "cloud_build" {
  for_each = merge(var.pipeline_triggers, var.component_triggers)
  # tflint-ignore: terraform_module_pinned_source
  source = "git@github.com:devoteamgcloud/accel-vertex-ai-cookiecutter-templates.git//terraform-modules/cloud_build"

  included      = each.value.included
  path          = each.value.path
  branch_regex  = each.value.branch_regex
  project_id    = var.project_id
  repo_owner    = var.repo_owner
  repo_name     = var.repo_name
  substitutions = local.cloud_build_substitutions[each.key]
  trigger_name  = each.key

  depends_on = [time_sleep.api_propagation]
}

resource "null_resource" "dummy_pipeline_job" {
  provisioner "local-exec" {
    command = "bash run_pipeline.sh"
    environment = {
      PROJECT = var.project_id
      REGION  = var.region
      TF_SA   = var.service_accounts["terraform"].email
    }
  }
  depends_on = [time_sleep.api_propagation]
}

module "run" {
  for_each = local.cloud_run

  source = "git@github.com:devoteamgcloud/tf-gcp-modules-cloud-run.git?ref=v1.0.0"
  project                 = var.project_id
  name                    = each.key
  location                = each.value.location
  service_account_email   = each.value.service_account_email
  cpu                     = each.value.cpu
  memory                  = each.value.memory
  max_instance_count      = each.value.max_instance_count
  min_instance_count      = each.value.min_instance_count
  startup_cpu_boost       = each.value.startup_cpu_boost
  timeout                 = each.value.timeout
  environment_variables   = each.value.environment_variables
  port                    = each.value.port
  iam                     = each.value.iam
  secrets                 = each.value.secrets
  traffic                 = each.value.traffic
  vpc_access_connector_id = each.value.vpc_access_connector_id

  depends_on = [time_sleep.api_propagation, module.basic]
}

module "basic" {
  source = "git@github.com:devoteamgcloud/accel-vertex-ai-cookiecutter-templates.git//terraform-modules/iam"

  groups           = var.groups
  projects         = local.project_iam
  service_accounts = local.all_service_accounts
  folders          = var.folders

  depends_on = [null_resource.dummy_pipeline_job]
}
