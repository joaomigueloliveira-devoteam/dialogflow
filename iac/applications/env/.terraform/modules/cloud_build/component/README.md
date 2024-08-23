# Vertex AI Accelerator Component template

This repository contains a template for a Vertex AI component, which is designed to be contained in a project generated from a base template.
This structure is meant to be as generic as possible. The generated folder is structured as follows:

```commandline
    components
    ├── your-component
    │    ├─ cloudbuild.yaml       # Build configuration
    │    ├─ Dockerfile            # Container build instructions
    │    ├─ main.py               # Component definition
    │    └─ requirements.txt      # Component requirements
    ├── another-component
    ├── ...
```

## Prerequisites

Generate your project repository from one of the base templates:

* Generate a [PoC repository](./poc/README.md)
* Generate a complete [project repository](./base/README.md)

## Add a component

In order to add a component to your project, go into the components folder of the repository and run:

```commandline
cookiecutter git+ssh://git@github.com/devoteamgcloud/accel-vertex-ai-foundations.git
```
then select the component template by choosing option 4.

This creates all the files needed for adding a new component to your project.
