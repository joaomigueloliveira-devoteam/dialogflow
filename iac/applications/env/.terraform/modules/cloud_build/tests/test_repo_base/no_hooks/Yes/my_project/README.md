# Vertex AI Accelerator Base Template

This repository contains a template for a Vertex AI project which is generated from this [template](https://github.com/devoteamgcloud/accel-vertex-ai-cookiecutter-templates).
This structure is meant to be as generic as possible. The repository structure is as follows:

```commandline
    .
    ├── pipelines                   # Folder containing all pipelines
    ├───── pipeline1
    ├───── pipeline2
    ├───── ...
    ├── components                  # Folder containing all components
    ├───── component1
    ├───── component2
    ├───── ...
    ├── iac                         # Folder containing the infrastructure as code
    ├───── env                      # Terraform module for one environment (dev, uat, prod)
    ├───── ops                      # Terraform module for ops project
    ├── .flake8                     # Contains flake8 conventions
    ├── .pre-commit-config.yaml     # Pre commit hooks
    └── README.md                   # You are here
```

## Getting started

In order to get started, you need to generate a pipeline. To start from scratch, you should go into the pipelines folder and run:

```commandline
cookiecutter git+ssh://git@github.com/devoteamgcloud/accel-vertex-ai-cookiecutter-templates.git --directory="pipeline"
```

This will generate the base template for your pipeline. You can then start working on it.
Should you need to generate custom components, you can use Cookiecutter to generate a template for that
in the components folder.
