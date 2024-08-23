data "google_project" "project" {}

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

  # IAM

  cloud_build_service_account = {
    email  = "${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
    create = false
  }

  service_accounts = merge(var.service_accounts, { "cloudbuild" : local.cloud_build_service_account })

  service_agents = {
    "aiplatform.googleapis.com" = {
      email  = "service-${data.google_project.project.number}@gcp-sa-aiplatform.iam.gserviceaccount.com"
      create = false
    },
    "cc-aiplatform.googleapis.com" = {
      email  = "service-${data.google_project.project.number}@gcp-sa-aiplatform-cc.iam.gserviceaccount.com"
      create = false
    },
    "cloudbuild.googleapis.com" = {
      email  = "service-${data.google_project.project.number}@gcp-sa-cloudbuild.iam.gserviceaccount.com"
      create = false
    },
    "compute.googleapis.com" = {
      email  = "${data.google_project.project.number}-compute@developer.gserviceaccount.com"
      create = false
    },
    "containerregistry.googleapis.com" = {
      email  = "service-${data.google_project.project.number}@containerregistry.iam.gserviceaccount.com"
      create = false
    },
    "ml.googleapis.com" = {
      email  = "service-${data.google_project.project.number}@cloud-ml.google.com.iam.gserviceaccount.com"
      create = false
    },
    "pubsub.googleapis.com" = {
      email  = "service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
      create = false
    },
    "run.googleapis.com" = {
      email  = "service-${data.google_project.project.number}@serverless-robot-prod.iam.gserviceaccount.com"
      create = false
    },
  }

  all_service_accounts = merge(local.service_agents, local.service_accounts)

  default_roles = {
    "aiplatform.googleapis.com" : ["roles/aiplatform.serviceAgent"],
    "cc-aiplatform.googleapis.com" : ["roles/aiplatform.customCodeServiceAgent"],
    "cloudbuild.googleapis.com" : ["roles/cloudbuild.serviceAgent"],
    "compute.googleapis.com" : ["roles/editor"],
    "containerregistry.googleapis.com" : ["roles/containerregistry.ServiceAgent"],
    "ml.googleapis.com" : ["roles/ml.serviceAgent"],
    "pubsub.googleapis.com" : ["roles/pubsub.serviceAgent"],
    "run.googleapis.com" : ["roles/run.serviceAgent"],
  }

  project_iam = {
    "my_project" = {
      "project_id" = var.project_id
      "groups"     = var.group_roles
      "sa"         = merge(var.service_account_roles, local.default_roles)
      "users"      = var.user_roles
    }
  }
}