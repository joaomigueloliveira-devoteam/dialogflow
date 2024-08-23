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
# module "vpc" {
#   for_each = var.vpc
#   source   = "../../modules/network/vpc"

#   project                        = each.value.project
#   description                    = each.value.description
#   subnets                        = each.value.subnets
#   routing_mode                   = each.value.routing_mode
#   skip_default_deny_fw           = lookup(each.value, "skip_default_deny_fw", false)
#   delete_default_route_on_create = true # Will be created by Terraform so it's managed and can be removed at a later time
#   firewall_logging_mode          = lookup(each.value, "firewall_logging_mode", null)


#   #namespace forced by module - no need in passing as will be overwritten anyway.
#   #to avoid using namespace, supply a custom label_order excluding it.
#   tenant      = lookup(each.value, "tenant", null)
#   environment = lookup(each.value, "environment", null)
#   stage       = lookup(each.value, "stage", null)
#   name        = lookup(each.value, "name", null)
#   attributes  = lookup(each.value, "attributes", null)
#   label_order = lookup(each.value, "label_order", null)
#   context     = module.this.context

# }

# module "firewalls" {
#   for_each            = var.firewalls
#   source              = "../../modules/network/firewall"
#   project             = each.value.project
#   network             = each.value.network
#   egress_allow_range  = lookup(each.value, "egress_allow_range", {})
#   ingress_allow_tag   = lookup(each.value, "ingress_allow_tag", {})
#   ingress_allow_range = lookup(each.value, "ingress_allow_range", {})
#   egress_deny_range   = lookup(each.value, "egress_deny_range", {})
#   depends_on          = [module.vpc]

#   #namespace forced by module - no need in passing as will be overwritten anyway.
#   #to avoid using namespace, supply a custom label_order excluding it.
#   tenant      = lookup(each.value, "tenant", null)
#   environment = lookup(each.value, "environment", null)
#   stage       = lookup(each.value, "stage", null)
#   name        = lookup(each.value, "name", null)
#   attributes  = lookup(each.value, "attributes", null)
#   label_order = lookup(each.value, "label_order", null)
#   context     = module.this.context
# }

resource "google_compute_region_network_endpoint_group" "serverless_neg" {
  provider              = google-beta
  name                  = "serverless-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = google_cloud_run_service.default.name
  }
}

resource "google_cloud_run_service" "default" {
  name     = "example"
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        image = "gcr.io/cloudrun/hello"
      }
    }
  }
  metadata {
    annotations = {
      # For valid annotation values and descriptions, see
      # https://cloud.google.com/sdk/gcloud/reference/run/deploy#--ingress
      "run.googleapis.com/ingress" = "all"
    }
  }
}

resource "google_cloud_run_service_iam_member" "public-access" {
  location = google_cloud_run_service.default.location
  project  = google_cloud_run_service.default.project
  service  = google_cloud_run_service.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_service_directory_namespace" "example" {
  provider     = google-beta
  namespace_id = "dialogflow"
  location     = var.region
}

resource "google_service_directory_service" "example" {
  provider   = google-beta
  service_id = "example-service"
  namespace  = google_service_directory_namespace.example.id

  metadata = {
    stage  = "prod"
    region = var.region
  }
}

resource "google_compute_http_health_check" "default" {
  name               = "http-health-check"
  request_path       = "/"
  check_interval_sec = 1
  timeout_sec        = 1
}

resource "google_compute_network" "ilb_network" {
  name                    = "l7-ilb-network"
  provider                = google-beta
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "proxy_subnet" {
  name          = "l7-ilb-proxy-subnet"
  provider      = google-beta
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  purpose       = "REGIONAL_MANAGED_PROXY"
  role          = "ACTIVE"
  network       = google_compute_network.ilb_network.id
}

resource "google_compute_subnetwork" "ilb_subnet" {
  name          = "l7-ilb-subnet"
  provider      = google-beta
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.ilb_network.id
}

resource "google_compute_region_ssl_certificate" "default" {
  region      = var.region
  name_prefix = "dialog-cert-"
  description = "a description"
  private_key = file("./server.key")
  certificate = file("./server.crt")

  lifecycle {
    create_before_destroy = true
  }
}

resource "google_compute_region_target_https_proxy" "default" {
  name             = "l7-ilb-target-http-proxy"
  url_map          = google_compute_region_url_map.default.id
  region           = var.region
  ssl_certificates = [google_compute_region_ssl_certificate.default.id]
}

resource "google_compute_region_url_map" "default" {
  provider = google-beta

  region          = var.region
  name            = "website-map"
  default_service = google_compute_region_backend_service.default.id
}

resource "google_compute_region_backend_service" "default" {
  provider = google-beta

  load_balancing_scheme = "INTERNAL_MANAGED"

  backend {
    group = google_compute_region_network_endpoint_group.serverless_neg.id
    balancing_mode = "UTILIZATION"
  }

  region      = var.region
  name        = "website-backend"
  protocol    = "HTTP"
}

resource "google_compute_forwarding_rule" "google_compute_forwarding_rule" {
  name                  = "l7-ilb-forwarding-rule"
  provider              = google-beta
  region                = var.region
  depends_on            = [google_compute_subnetwork.proxy_subnet]
  # ip_protocol           = "TCP"
  load_balancing_scheme = "INTERNAL_MANAGED"
  port_range            = "443"
  target                = google_compute_region_target_https_proxy.default.id
  network               = google_compute_network.ilb_network.id
  subnetwork            = google_compute_subnetwork.ilb_subnet.id
  # network_tier          = "PREMIUM"
  service_directory_registrations {
    namespace = google_service_directory_namespace.example.namespace_id
    service   = google_service_directory_service.example.service_id
  }
}
