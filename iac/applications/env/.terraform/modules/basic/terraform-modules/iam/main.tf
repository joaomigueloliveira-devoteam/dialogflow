module "service_accounts" {
  for_each = {
    for sa_name, sa in var.service_accounts : sa_name => sa if sa.create
  }

  source = "git@github.com:devoteamgcloud/tf-gcp-modules-service-account.git//service_account?ref=v1.0.0"

  project      = each.value.gcp_project_id
  display_name = each.value.display_name
  description  = each.value.description
  disabled     = each.value.disabled

  #namespace forced by module - no need in passing as will be overwritten anyway.
  #to avoid using namespace, supply a custom label_order excluding it.
  tenant      = lookup(each.value, "tenant", null)
  environment = lookup(each.value, "environment", null)
  stage       = lookup(each.value, "stage", null)
  name        = lookup(each.value, "name", null)
  attributes  = lookup(each.value, "attributes", null)
  label_order = lookup(each.value, "label_order", null)
  context     = module.this.context

}

module "service_accounts_policy" {
  for_each = local.service_account_bindings

  source = "git@github.com:devoteamgcloud/tf-gcp-modules-service-account.git//service_account_policy?ref=v1.0.0"

  service_account_id = each.value.service_account_id
  bindings           = each.value.bindings
}

module "folder" {
  for_each = local.folder_bindings

  source = "git@github.com:devoteamgcloud/tf-gcp-modules-iam-folder.git//iam_folder_policy?ref=v1.0.0"

  folder_id = each.value.folder_id
  bindings  = each.value.bindings
}

module "projects" {
  for_each = local.project_bindings

  source = "git@github.com:devoteamgcloud/tf-gcp-modules-iam-project.git//iam_project_policy?ref=v1.0.0"

  project_id = each.value.project_id
  bindings   = each.value.bindings
}
