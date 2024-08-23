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

  {% if cookiecutter['include_iam'] == "Yes" %}depends_on = [time_sleep.api_propagation, module.basic]{% else %}depends_on = [time_sleep.api_propagation]{% endif %}
}
{% if cookiecutter['include_iam'] == "Yes" %}
module "basic" {
  source = "git@github.com:devoteamgcloud/accel-vertex-ai-cookiecutter-templates.git//terraform-modules/iam"

  groups           = var.groups
  projects         = local.project_iam
  service_accounts = local.all_service_accounts
  folders          = var.folders

  depends_on = [null_resource.dummy_pipeline_job]
}{% endif %}
