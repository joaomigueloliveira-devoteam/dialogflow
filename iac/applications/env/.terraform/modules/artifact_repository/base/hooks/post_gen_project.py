"""Generates Tfvars and Backend files for each environment from a template."""
from cookiecutter import prompt
from jinja2 import Template
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
_OPS_PATH = os.path.join(_ROOT_PATH, "ops")
tfvars_template = os.path.join(_ENV_PATH, "template.tfvars.json")
backend_template = os.path.join(_ENV_PATH, "template.backend")
locals_template = os.path.join(_ROOT_PATH, "locals_template.tf")

environments = {
    "dev": {
        "terraform_service_account": "{{ cookiecutter['tf_sa_dev'] }}",
        "gcp_project_id": "{{ cookiecutter['project_id_dev'] }}",
        "terraform_state_bucket": "{{ cookiecutter['tfstate_bucket_dev'] }}",
    },
    "uat": {
        "terraform_service_account": "{{ cookiecutter['tf_sa_uat'] }}",
        "gcp_project_id": "{{ cookiecutter['project_id_uat'] }}",
        "terraform_state_bucket": "{{ cookiecutter['tfstate_bucket_uat'] }}",
    },
    "prod": {
        "terraform_service_account": "{{ cookiecutter['tf_sa_prod'] }}",
        "gcp_project_id": "{{ cookiecutter['project_id_prod'] }}",
        "terraform_state_bucket": "{{ cookiecutter['tfstate_bucket_prod'] }}",
    },
}

with open(tfvars_template) as template_file:
    template = template_file.read()
    for env, env_context in environments.items():
        with open(os.path.join(_ENV_PATH, f"{env}.tfvars.json"), "w") as f2:
            f2.write(Template(template).render(env_context))

with open(backend_template) as template_file:
    template = template_file.read()
    for env, env_context in environments.items():
        with open(os.path.join(_ENV_PATH, f"{env}.backend"), "w") as f2:
            f2.write(Template(template).render(env_context))

with open(locals_template) as template_file:
    template = template_file.read()
    for app, path in zip(["env", "ops"], [_ENV_PATH, _OPS_PATH]):
        with open(os.path.join(path, "locals.tf"), "w") as f2:
            f2.write(
                Template(template).render(
                    {"app": app, "project_name": "{{ cookiecutter['project_folder'] }}"}
                )
            )

os.remove(tfvars_template)
os.remove(backend_template)
os.remove(locals_template)

{% if cookiecutter['include_iam'] == "Yes" %}

questions = []

for env in list(environments.keys()) + ["ops"]:
    questions.append(f"Add {env} project groups")
    questions.append(f"Add {env} project users")

count_questions = 0
for env in list(environments.keys()) + ["ops"]:
    if env == "ops":
        path = os.path.join(_OPS_PATH, "ops.tfvars.json")
    else:
        path = os.path.join(_ENV_PATH, f"{env}.tfvars.json")
    with open(path, "r") as f:
        var_file = json.load(f)

    count_questions += 1
    use_groups = prompt.read_user_yes_no(
        var_name=questions[count_questions - 1], default_value="Yes", prefix=f"  [dim][{count_questions}/{len(questions)}][/] "
    )

    if use_groups:

        def inner_func(env, exit_condition, prefix=""):
            """Inner loop for groups prompt."""
            email = prompt.read_user_variable(
                var_name=f"{env} group email", default_value="your.group@devoteam.com", prefix=f"  [dim][{count_questions}/{len(questions)}][/] "
            )

            roles = custom_prompt.read_user_variable_list(
                var_name="group roles", exit_condition=exit_condition, prefix=f"  [dim][{count_questions}/{len(questions)}][/] "
            )
            return email, roles

        exit_condition = "Press enter to exit"
        groups = custom_prompt.read_user_variable_json(
            var_name=f"{env} group name",
            exit_condition=exit_condition,
            inner_func=inner_func,
            inner_func_args={"env": env, "exit_condition": exit_condition,},
            prefix=f"  [dim][{count_questions}/{len(questions)}][/] "
        )

        var_file["groups"] = {
            name: {"email": email} for name, (email, _) in groups.items()
        }
        var_file["group_roles"] = {name: roles for name, (_, roles) in groups.items()}

    count_questions += 1
    use_users = prompt.read_user_yes_no(
        var_name=f"Add {env} project users", default_value="Yes", prefix=f"  [dim][{count_questions}/{len(questions)}][/] "
    )

    if use_users:
        exit_condition = "Press enter to exit"
        users = custom_prompt.read_user_variable_json(
            var_name=questions[count_questions - 1],
            exit_condition=exit_condition,
            inner_func=custom_prompt.read_user_variable_list,
            inner_func_args={
                "var_name": "user roles",
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
import google.auth
from google.auth import impersonated_credentials
import google.auth.transport.requests
from google.cloud import storage
from googleapiclient import discovery

environments["ops"] = {
    "terraform_service_account": "{{ cookiecutter['tf_sa_ops'] }}",
    "gcp_project_id": "{{ cookiecutter['project_id_ops'] }}",
    "terraform_state_bucket": "{{ cookiecutter['tfstate_bucket_ops'] }}",
}

credentials, project_id = google.auth.default()

target_scopes = ['https://www.googleapis.com/auth/cloud-platform']

for env, config in environments.items():

    target_credentials = impersonated_credentials.Credentials(
        source_credentials=credentials,
        target_principal=config["terraform_service_account"],
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
    apis.enable(name=f"projects/{config['gcp_project_id']}/services/cloudresourcemanager.googleapis.com").execute()
    print(f"\nCloud Resource Manager API was enabled for project {config['gcp_project_id']}")

    gcs_client = storage.Client(project=config["gcp_project_id"], credentials=target_credentials)
    bucket = gcs_client.get_bucket(config["terraform_state_bucket"])
    bucket.versioning_enabled = True
    bucket.patch()

    print(f"Versioning was enabled for bucket {bucket.name}")

{% endif %}
