locals {

  service_account_bindings = {
    for sa_name, service_account in var.service_accounts : sa_name => {
      service_account_id = lookup(module.service_accounts, sa_name, null) == null ? "projects/-/serviceAccounts/${var.service_accounts[sa_name].email}" : module.service_accounts[sa_name].id
      bindings = transpose(merge(
        {
          for sa, roles in service_account.sa : lookup(module.service_accounts, sa, null) == null ? "serviceAccount:${var.service_accounts[sa].email}" : "serviceAccount:${module.service_accounts[sa].email}" => roles
        },
        {
          for group, roles in service_account.groups : "group:${var.groups[group]["email"]}" => roles
        },
        {
          for user, roles in service_account.users : "user:${user}" => roles
        }
      ))
    } if(contains(keys(service_account), "groups") && length(service_account.groups) > 0) || (contains(keys(service_account), "sa") && length(service_account.sa) > 0)
  }

  folder_bindings = {
    for folder_name, folder in var.folders : folder_name => {
      folder_id = folder.folder_id
      bindings = transpose(merge(
        {
          for sa, roles in folder.sa : lookup(module.service_accounts, sa, null) == null ? "serviceAccount:${var.service_accounts[sa].email}" : "serviceAccount:${module.service_accounts[sa].email}" => roles
        },
        {
          for group, roles in folder.groups : "group:${var.groups[group]["email"]}" => roles
        },
        {
          for user, roles in folder.users : "user:${user}" => roles
        }
      ))
    }
  }

  project_bindings = {
    for project_name, project in var.projects : project_name => {
      project_id = project.project_id
      bindings = transpose(merge(
        {
          for sa, roles in project.sa : lookup(module.service_accounts, sa, null) == null ? "serviceAccount:${var.service_accounts[sa].email}" : "serviceAccount:${module.service_accounts[sa].email}" => roles
        },
        {
          for group, roles in project.groups : "group:${var.groups[group]["email"]}" => roles
        },
        {
          for user, roles in project.users : "user:${user}" => roles
        }
      ))
    }
  }
}