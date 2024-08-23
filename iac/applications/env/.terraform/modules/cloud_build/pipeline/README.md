# Vertex AI Accelerator Pipeline template

This repository contains a template for a Vertex AI pipeline, which is designed to be contained in a project generated from a base template.
This structure is meant to be as generic as possible. The generated folder is structured as follows:

```commandline
    pipelines
    ├── your-pipeline
    │    ├─ cloudbuild.yaml          # Build configuration
    │    ├─ pipeline.py              # Pipeline definition
    │    └─ requirements.txt         # Build requirements
    ├── another-pipeline
    ├── ...
```

## Prerequisites

Generate your project repository from one of the base templates:

* Generate a [PoC repository](./poc/README.md)
* Generate a complete [project repository](./base/README.md)

## Add a component

In order to add a pipeline to your project, go into the pipelines folder of the repository you just generated and run:

```commandline
cookiecutter git+ssh://git@github.com/devoteamgcloud/accel-vertex-ai-foundations.git
```
then select the pipeline template by choosing option 3.

This creates all the files needed for adding a new pipeline to your project.
