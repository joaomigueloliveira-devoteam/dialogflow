"""Check if pipeline name is valid."""

import os
import json
import re
import sys
import yaml

_ROOT_PATH = os.sep.join(os.getcwd().split(os.sep)[:-2])
_IAC_PATH = os.path.join(_ROOT_PATH, "iac", "applications")
_ENV_PATH = os.path.join(_IAC_PATH, "env")

_VALID_AR_PIPELINE_PATTERN = re.compile("^[a-z][a-z0-9-]{3,127}$")

if not re.match(_VALID_AR_PIPELINE_PATTERN, "{{cookiecutter['pipeline_name']}}"):
    print(
        'ERROR: "{{cookiecutter['pipeline_name']}}" is not a valid pipeline template name. The name may contain lowercase letters, numbers and "-", should start with a letter and be between 4 and 128 characters long.'
    )

    sys.exit(1)

with open(os.path.join(_ROOT_PATH, ".vertex-ai-foundations.yaml"), "r") as f:
    config = yaml.safe_load(f)["config"]

if config["poc"]:
    tfvars = ["poc.tfvars.json"]

else:
    tfvars = ["dev.tfvars.json", "uat.tfvars.json", "prod.tfvars.json"]

for file in tfvars:
    with open(os.path.join(_ENV_PATH, file), "r") as f:
        var_file = json.load(f)

    if "{{cookiecutter['pipeline_sa']}}" in var_file["service_accounts"].keys():
        print(
            'ERROR: "A service account with name {{cookiecutter['pipeline_sa']}}" already esists. Choose a different name.'
        )

        sys.exit(1)
