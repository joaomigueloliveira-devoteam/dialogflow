{% if app == "env" %}data "google_project" "project" {}

locals {

  cloud_run = { for k, v in var.cloud_run : k => merge(v, {
    service_account_email = try(module.basic.service_accounts[v.service_account].email, var.service_accounts[v.service_account].email)
    iam = merge(
      merge([for sa, roles in v.sa : { for role in roles : "${sa}/${role}" => {
        member = "serviceAccount:${try(module.basic.service_accounts[sa].email, var.service_accounts[sa].email)}"
        role   = role
      } }]...),
      merge([for user, roles in v.users : { for role in roles : "${user}/${role}" => {
        member = "user:${user}"
        role   = role
      } }]...),
      merge([for group, roles in v.groups : { for role in roles : "${group}/${role}" => {
        member = "group:${group}"
        role   = role
      } }]...)
    )})
  }
{% else %}data "google_project" "env_projects" {
  for_each = var.env_projects

  project_id = each.value
}

data "google_project" "project" {}

locals {
  vertex_ai_service_agents    = [for project in data.google_project.env_projects : "serviceAccount:service-${project.number}@gcp-sa-aiplatform.iam.gserviceaccount.com"]
  vertex_ai_cc_service_agents = [for project in data.google_project.env_projects : "serviceAccount:service-${project.number}@gcp-sa-aiplatform-cc.iam.gserviceaccount.com"]

  all_vertex_ai_agents = concat(local.vertex_ai_service_agents, local.vertex_ai_cc_service_agents)

  updated_artifact_registry_maps = {
    for artifact_repo_name, artifact_repo_content in var.artifact_registry_repositories : artifact_repo_name => {
      location    = artifact_repo_content.location
      description = artifact_repo_content.description
      format      = artifact_repo_content.format
      role_group_map = lookup(artifact_repo_content.role_group_map, "roles/artifactregistry.reader", null) != null ? tomap({
        for role, groups in artifact_repo_content.role_group_map : role => role == "roles/artifactregistry.reader" ? tolist(set(concat(groups, local.all_vertex_ai_agents))) : groups
        }) : tomap({
        "roles/artifactregistry.reader" = tolist(local.all_vertex_ai_agents)
      })
    }
  }
  cloud_build_substitutions = merge(
    { for trigger_name, config in merge(var.pipeline_triggers, var.component_triggers) : trigger_name => merge(config.substitutions, {
      "_PROJECT_ROOT"                     = "{{ project_name }}"
      "_REGION"                           = var.region
      "_ARTIFACT_REGISTRY_CONTAINERS_URL" = "${var.artifact_registry_repositories["pipeline-containers"].location}-docker.pkg.dev/${var.project_id}/pipeline-containers"
      "_ARTIFACT_REGISTRY_TEMPLATES_URL"  = "https://${var.artifact_registry_repositories["pipeline-templates"].location}-kfp.pkg.dev/${var.project_id}/pipeline-templates"
    }) }
  ){% endif %}
  # IAM

  cloud_build_service_account = {
    email  = "${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
    create = false
  }

  {% if app == "env" %}service_accounts = merge(var.service_accounts, { "cloudbuild" : local.cloud_build_service_account }){% else %}service_accounts = merge(
    var.service_accounts,
    { "cloudbuild" : local.cloud_build_service_account },
    {
      for project in data.google_project.env_projects : project.project_id => {
        email  = "service-${project.number}@gcp-sa-aiplatform.iam.gserviceaccount.com"
        create = false
      }
    }
  ){% endif %}

  service_agents = {
    {% if app == "env" %}"aiplatform.googleapis.com" = {
      email  = "service-${data.google_project.project.number}@gcp-sa-aiplatform.iam.gserviceaccount.com"
      create = false
    },
    "cc-aiplatform.googleapis.com" = {
      email  = "service-${data.google_project.project.number}@gcp-sa-aiplatform-cc.iam.gserviceaccount.com"
      create = false
    },{% else %}"artifactregistry.googleapis.com" = {
      email  = "service-${data.google_project.project.number}@gcp-sa-artifactregistry.iam.gserviceaccount.com"
      create = false
    },{% endif %}
    "cloudbuild.googleapis.com" = {
      email  = "service-${data.google_project.project.number}@gcp-sa-cloudbuild.iam.gserviceaccount.com"
      create = false
    },{% if app == "env" %}
    "compute.googleapis.com" = {
      email  = "${data.google_project.project.number}-compute@developer.gserviceaccount.com"
      create = false
    },{% endif %}
    "containerregistry.googleapis.com" = {
      email  = "service-${data.google_project.project.number}@containerregistry.iam.gserviceaccount.com"
      create = false
    },{% if app == "env" %}
    "ml.googleapis.com" = {
      email  = "service-${data.google_project.project.number}@cloud-ml.google.com.iam.gserviceaccount.com"
      create = false
    },{% endif %}
    "pubsub.googleapis.com" = {
      email  = "service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
      create = false
    },{% if app == "env" %}
    "run.googleapis.com" = {
      email  = "service-${data.google_project.project.number}@serverless-robot-prod.iam.gserviceaccount.com"
      create = false
    },{% endif %}
  }

  all_service_accounts = merge(local.service_agents, local.service_accounts)

  default_roles = {
    {% if app == "env" %}"aiplatform.googleapis.com" : ["roles/aiplatform.serviceAgent"],
    "cc-aiplatform.googleapis.com" : ["roles/aiplatform.customCodeServiceAgent"],
    {% else %}"artifactregistry.googleapis.com" : ["roles/artifactregistry.serviceAgent"],
    {% endif %}"cloudbuild.googleapis.com" : ["roles/cloudbuild.serviceAgent"],{% if app == "env" %}
    "compute.googleapis.com" : ["roles/editor"],{% endif %}
    "containerregistry.googleapis.com" : ["roles/containerregistry.ServiceAgent"],{% if app == "env" %}
    "ml.googleapis.com" : ["roles/ml.serviceAgent"],{% endif %}
    "pubsub.googleapis.com" : ["roles/pubsub.serviceAgent"],{% if app == "env" %}
    "run.googleapis.com" : ["roles/run.serviceAgent"],{% endif %}
  }
{% if app == "ops" %}
  ar_reader_roles = {
    for project in data.google_project.env_projects : project.project_id => ["projects/${var.project_id}/roles/artifactRegistryUser"]
  }
{% endif %}
  project_iam = {
    "my_project" = {
      "project_id" = var.project_id
      "groups"     = var.group_roles
      "sa"         = merge(var.service_account_roles, local.default_roles{% if app == "ops" %}, local.ar_reader_roles{% endif %})
      "users"      = var.user_roles
    }
  }
}
