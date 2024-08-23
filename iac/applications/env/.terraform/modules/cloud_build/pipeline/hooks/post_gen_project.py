"""Add buckets to tfvars."""
import os
import json
import yaml
from cookiecutter import prompt

try:
    from cookiecutter_utils import custom_prompt, gcp_templates
except ImportError:
    import sys
    import subprocess

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "git+ssh://git@github.com/devoteamgcloud/accel-vertex-ai-cookiecutter-templates.git#egg=cookiecutter_utils&subdirectory=cookiecutter_utils",
        ]
    )

    from cookiecutter_utils import custom_prompt, gcp_templates

from cookiecutter_utils.gcp_templates import (
    _DEFAULT_PIPELINE_SA_ROLES,
    _DEFAULT_CLOUDBUILD_SA_ROLES,
)

_TF_BUCKET_NAME = "{project_id}-pipelines-{pipeline_name}"

_ROOT_PATH = os.sep.join(os.getcwd().split(os.sep)[:-2])
_ROOT_FOLDER = _ROOT_PATH.split(os.sep)[-1]
_IAC_PATH = os.path.join(_ROOT_PATH, "iac", "applications")
_ENV_PATH = os.path.join(_IAC_PATH, "env")
_OPS_PATH = os.path.join(_IAC_PATH, "ops")

with open(os.path.join(_ROOT_PATH, ".vertex-ai-foundations.yaml"), "r") as f:
    config = yaml.safe_load(f)["config"]

if config["poc"]:
    _OPS_PATH = _ENV_PATH

    env_variables = {
        "poc": {
            "tfvars": "poc.tfvars.json",
            "regex": ".*",
        }
    }

else:
    env_variables = {
        "dev": {
            "tfvars": "dev.tfvars.json",
            "regex": ".*",
        },
        "uat": {
            "tfvars": "uat.tfvars.json",
            "regex": "release.*",
        },
        "prod": {
            "tfvars": "prod.tfvars.json",
            "regex": "main",
        },
    }

questions = []

# Dev, uat, prod questions
for env in list(env_variables.keys()):
    questions.append(f"{env} SA users")
    questions.append(f"{env} pipeline SA roles")

# Ops questions
questions.append("Cloud Build SA roles")
for env in list(env_variables.keys()):
    questions.append(f"branch regex to fire {env} trigger")

count_questions = 0

# env terraform
for env, variables in env_variables.items():
    with open(os.path.join(_ENV_PATH, variables["tfvars"]), "r") as f:
        var_file = json.load(f)

    project_id = var_file["project_id"]
    region = var_file["region"]
    env_variables[env]["project_id"] = project_id

    # Bucket
    pipeline_bucket = gcp_templates.gcs_bucket_template(
        name=_TF_BUCKET_NAME.format(
            pipeline_name="{{cookiecutter['pipeline_name']}}".replace("_", "-"),
            project_id=project_id,
        ),
        region=region,
    )
    var_file["buckets"]["{{cookiecutter['pipeline_name']}}"] = pipeline_bucket

    if var_file["include_iam"]:
        # SA users
        count_questions += 1
        variables["pipeline_sa_users"] = custom_prompt.read_user_variable_list(
            var_name=questions[count_questions - 1],
            exit_condition="Press enter to exit",
            prefix=f"  [dim][{count_questions}/{len(questions)}][/] ",
        )

        # SA roles
        variables["pipeline_sa_roles"] = list(_DEFAULT_PIPELINE_SA_ROLES)
        print("\nDefault pipeline SA roles:")
        print(*variables["pipeline_sa_roles"], sep="\n")

        count_questions += 1
        variables["pipeline_sa_roles"].extend(
            custom_prompt.read_user_variable_list(
                var_name=questions[count_questions - 1],
                exit_condition="Add a role or press enter to exit",
                prefix=f"  [dim][{count_questions}/{len(questions)}][/] ",
            )
        )

        # SA
        pipeline_sa = gcp_templates.service_account_template(
            name="{{cookiecutter['pipeline_sa']}}",
            users=variables["pipeline_sa_users"],
        )

        var_file["service_accounts"]["{{cookiecutter['pipeline_sa']}}"] = pipeline_sa
        var_file["service_account_roles"][
            "{{cookiecutter['pipeline_sa']}}"
        ] = variables["pipeline_sa_roles"]

    with open(os.path.join(_ENV_PATH, variables["tfvars"]), "w") as f:
        json.dump(var_file, f, indent=4)


if config["poc"]:
    tfvars = env_variables["poc"]["tfvars"]
else:
    # ops terraform
    tfvars = "ops.tfvars.json"

with open(os.path.join(_OPS_PATH, tfvars), "r") as f:
    var_file = json.load(f)

if var_file["include_iam"]:
    # SA roles
    cloudbuild_sa_roles = var_file["service_account_roles"]["cloudbuild"]
    if len(cloudbuild_sa_roles) == 1:
        cloudbuild_sa_roles.extend(_DEFAULT_CLOUDBUILD_SA_ROLES)

    print("\nDefault Cloud Build SA roles:")
    print(*cloudbuild_sa_roles, sep="\n")

    count_questions += 1
    cloudbuild_sa_roles.extend(
        custom_prompt.read_user_variable_list(
            var_name=questions[count_questions - 1],
            exit_condition="Add a role or press enter to exit",
            prefix=f"  [dim][{count_questions}/{len(questions)}][/] ",
        )
    )

for env, variables in env_variables.items():

    # Trigger branch
    count_questions += 1
    env_variables[env]["regex"] = prompt.read_user_variable(
        var_name=questions[count_questions - 1],
        default_value=variables["regex"],
        prefix=f"  [dim][{count_questions}/{len(questions)}][/] ",
    )

    # Trigger substitutions
    substitutions = {
        "_PROJECT_ID": variables["project_id"],
        "_PIPELINE_NAME": "{{cookiecutter['pipeline_name']}}",
    }

    # Trigger
    trigger = gcp_templates.cloudbuild_trigger_template(
        included=["pipelines/{{cookiecutter['pipeline_name']}}/**"],
        path="pipelines/{{cookiecutter['pipeline_name']}}/cloudbuild.yaml",
        substitutions=substitutions,
        branch_regex=variables["regex"],
    )
    var_file["pipeline_triggers"][
        env + "-{{cookiecutter['pipeline_name']}}".replace("_", "-")
    ] = trigger

with open(os.path.join(_OPS_PATH, tfvars), "w") as f:
    json.dump(var_file, f, indent=4)
