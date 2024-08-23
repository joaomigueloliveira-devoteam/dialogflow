
module "labels" {
  source    = "cloudposse/label/null"
  version   = "0.25.0"
  namespace = "sa"
  context   = module.this.context
}

resource "google_service_account" "service_account" {
  project      = var.project
  account_id   = module.labels.id
  display_name = var.display_name
  description  = var.description != "" ? var.description : var.display_name != "" ? var.display_name : module.labels.id
}
