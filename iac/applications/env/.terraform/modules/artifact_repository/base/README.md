# Vertex AI project template

This repository contains a template for a Vertex AI project. This structure is meant to be as generic as possible. The generated folder is structured as follows:

```commandline
    your-project
    ├── iac
    │    └─ applications
    │         ├─ env
    │         │    ├─ locals.tf
    │         │    ├─ main.tf
    │         │    ├─ variables.tf
    │         │    ├─ version.tf
    │         │    ├─ dev.backend
    │         │    ├─ uat.backend
    │         │    ├─ prod.backend
    │         │    ├─ dev.tfvars.json
    │         │    ├─ uat.tfvars.json
    │         │    ├─ prod.tfvars.json
    │         │    ├─ run_pipeline.sh
    │         │    └─ README.md
    │         ├─ ops
    │         │    ├─ locals.tf
    │         │    ├─ main.tf
    │         │    ├─ variables.tf
    │         │    ├─ version.tf
    │         │    ├─ ops.backend
    │         │    ├─ ops.tfvars.json
    │         │    └─ README.md
    │         └─ apply_infra.sh
    ├── pipelines
    │    ├─ ...
    ├── components
    │    ├─ ...
    ├── .flake8
    ├── .pre-commit-config.yaml
    ├── .vertex-ai-foundations.yaml
    ├── README.md
```

## Prerequisites

Before you can deploy the base cookiecutter, you need to have the necessary projects
and permissions in GCP.

This template uses 3 environments for deploying pipelines: **dev, uat and prod**. These projects
will be where your pipelines will run. In order to run, pipelines need templates and component images.
This is why you will also need to have one **ops** project to host those.

For each project (dev, uat, prod and ops) create the following:
* A project on GCP
* A service account on that project (easiest is to just call it `terraform@{PROJECT_ID}.iam.gserviceaccount.com)`
* Give permissions to the service account:
  * Quota Administrator
  * Security Admin
  * Storage Admin
  * Vertex AI User (only for dev, uat and prod)
  * Artifact Registry Administrator (only for ops)
  * Cloud Build Editor (only for ops)
  * Role Administrator (only for ops)
* A bucket to hold the terraform state (easiest is to just call it `gcs-{PROJECT_ID}-tfstate`)
* Ensure you have the **Service Account Token Creator** on role on the service account

Then ensure that the Ops Terraform service account has Viewer access to the dev, uat and prod projects.

## Usage

Generate an empty repository from the base
module. You can do this by running

```commandline
cookiecutter git+ssh://git@github.com/devoteamgcloud/accel-vertex-ai-foundations.git
```
and selecting the base template by choosing option 2.