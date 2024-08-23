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

  all_vertex_ai_agents = [
    "serviceAccount:service-${data.google_project.project.number}@gcp-sa-aiplatform.iam.gserviceaccount.com",
    "serviceAccount:service-${data.google_project.project.number}@gcp-sa-aiplatform-cc.iam.gserviceaccount.com"
  ]

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
      "_PROJECT_ROOT"                     = "my_project"
      "_REGION"                           = var.region
      "_ARTIFACT_REGISTRY_CONTAINERS_URL" = "${var.artifact_registry_repositories["pipeline-containers"].location}-docker.pkg.dev/${var.project_id}/pipeline-containers"
      "_ARTIFACT_REGISTRY_TEMPLATES_URL"  = "https://${var.artifact_registry_repositories["pipeline-templates"].location}-kfp.pkg.dev/${var.project_id}/pipeline-templates"
    }) }
  )
}
