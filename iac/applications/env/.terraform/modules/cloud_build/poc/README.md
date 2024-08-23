# Vertex AI PoC template

This repository contains a template for a Vertex AI PoC. This structure is meant to be as generic as possible. The generated folder is structured as follows:

```commandline
    your-project
    ├── iac
    │    └─ applications
    │         └─ env
    │             ├─ locals.tf
    │             ├─ main.tf
    │             ├─ variables.tf
    │             ├─ version.tf
    │             ├─ poc.backend
    │             ├─ poc.tfvars.json
    │             ├─ run_pipeline.sh
    │             └─ README.md
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

Before you can deploy the base cookiecutter, you need to have the necessary project
and permissions in GCP.

This template uses one environment for running Vertex AI jobs and store artifacts.

Create the following:
* A project on GCP
* A service account on that project (easiest is to just call it `terraform@{PROJECT_ID}.iam.gserviceaccount.com)`
* Give permissions to the service account:
  * Artifact Registry Administrator
  * Cloud Build Editor
  * Quota Administrator
  * Role Administrator
  * Security Admin
  * Storage Admin
  * Vertex AI User
* A bucket to hold the terraform state (easiest is to just call it `gcs-{PROJECT_ID}-tfstate`)
* Ensure you have the **Service Account Token Creator** on role on the service account

## Usage

Generate an empty repository from the base
module. You can do this by running

```commandline
cookiecutter git+ssh://git@github.com/devoteamgcloud/accel-vertex-ai-foundations.git
```
and selecting the PoC template by choosing option 1.

This will lay out the basic repository structure and get you started with the project.