"""Generates Tfvars and Backend files for each environment from a template."""
from cookiecutter import prompt
import json
import os
import sys

try:
    from cookiecutter_utils import custom_prompt
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

    from cookiecutter_utils import custom_prompt

_ROOT_PATH = os.path.join("iac", "applications")
_ENV_PATH = os.path.join(_ROOT_PATH, "env")

{% if cookiecutter['include_iam'] == "Yes" %}

questions = []

questions.append("Add project groups")
questions.append("Add project users")

count_questions = 0
path = os.path.join(_ENV_PATH, "poc.tfvars.json")
with open(path, "r") as f:
    var_file = json.load(f)

count_questions += 1
use_groups = prompt.read_user_yes_no(
    var_name=questions[count_questions - 1], default_value="Yes", prefix=f"  [dim][{count_questions}/{len(questions)}][/] "
)

if use_groups:

    def inner_func(exit_condition, prefix=""):
        """Inner loop for groups prompt."""
        email = prompt.read_user_variable(
            var_name=f"Group email", default_value="your.group@devoteam.com", prefix=f"  [dim][{count_questions}/{len(questions)}][/] "
        )

        roles = custom_prompt.read_user_variable_list(
            var_name="Group roles", exit_condition=exit_condition, prefix=f"  [dim][{count_questions}/{len(questions)}][/] "
        )
        return email, roles

    exit_condition = "Press enter to exit"
    groups = custom_prompt.read_user_variable_json(
        var_name=f"Group name",
        exit_condition=exit_condition,
        inner_func=inner_func,
        inner_func_args={"exit_condition": exit_condition,},
        prefix=f"  [dim][{count_questions}/{len(questions)}][/] "
    )

    var_file["groups"] = {
        name: {"email": email} for name, (email, _) in groups.items()
    }
    var_file["group_roles"] = {name: roles for name, (_, roles) in groups.items()}

count_questions += 1
use_users = prompt.read_user_yes_no(
    var_name=f"Add project users", default_value="Yes", prefix=f"  [dim][{count_questions}/{len(questions)}][/] "
)

if use_users:
    exit_condition = "Press enter to exit"
    users = custom_prompt.read_user_variable_json(
        var_name=questions[count_questions - 1],
        exit_condition=exit_condition,
        inner_func=custom_prompt.read_user_variable_list,
        inner_func_args={
            "var_name": "User roles",
            "exit_condition": exit_condition,
        },
        prefix=f"  [dim][{count_questions}/{len(questions)}][/] ",
    )

    var_file["user_roles"] = users

with open(path, "w") as f:
    json.dump(var_file, f, indent=4)
{% endif %}
# The following code is not generated during tests
{% if not cookiecutter['_test'] %}
import google
import google.auth
from google.auth import impersonated_credentials
import google.auth.transport.requests
from google.cloud import storage
from googleapiclient import discovery

credentials, project_id = google.auth.default()

target_scopes = ['https://www.googleapis.com/auth/cloud-platform']

target_credentials = impersonated_credentials.Credentials(
    source_credentials=credentials,
    target_principal="{{ cookiecutter['tf_sa'] }}",
    target_scopes=target_scopes,
    lifetime=60
)

services = discovery.build(
    "serviceusage",
    "v1",
    cache_discovery=False,
    credentials=target_credentials,
)

apis = services.services()
apis.enable(name="projects/{{ cookiecutter['project_id'] }}/services/cloudresourcemanager.googleapis.com").execute()
print("\nCloud Resource Manager API was enabled for project {{ cookiecutter['project_id'] }}")


gcs_client = storage.Client(project="{{ cookiecutter['project_id'] }}", credentials=target_credentials)
bucket = gcs_client.get_bucket("{{ cookiecutter['tfstate_bucket'] }}")
bucket.versioning_enabled = True
bucket.patch()

print(f"Versioning was enabled for bucket {bucket.name}")
{% endif %}
