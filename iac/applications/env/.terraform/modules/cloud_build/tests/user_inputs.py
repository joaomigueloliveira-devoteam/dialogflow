"""Constants for mocked user inputs."""

import pytest
from io import StringIO

# Templates

_TEMPLATES = {
    "poc": "PoC IaC (poc)",
    "base": "Project IaC (base)",
    "pipeline": "Pipeline (pipeline)",
    "component": "Component (component)",
}

# Cloud Build template for testing

_TRIGGER_INCLUDED = ["path/to/folder/**"]
_TRIGGER_PATH = "path/to/cloudbuild.yaml"
_TRIGGER_SUBSTITUTIONS = {"_SUB_KEY": "sub_value"}
_TRIGGER_BRANCH_REGEX = ".*"
_TRIGGER_TEMPLATE = {
    "included": _TRIGGER_INCLUDED,
    "path": _TRIGGER_PATH,
    "substitutions": _TRIGGER_SUBSTITUTIONS,
    "branch_regex": _TRIGGER_BRANCH_REGEX,
}

# GCS bucket template for testing

_BUCKET_NAME = "bucket"
_BUCKET_REGION = "europe-west1"
_BUCKET_TEMPLATE = {"name": _BUCKET_NAME, "region": _BUCKET_REGION}

# Pipeline service account template for testing

_SA_NAME = "sa"
_SA_USERS = ["user1@devoteam.com", "user2@devoteam.com"]
_SA_USER_ROLE = "roles/iam.serviceAccountUser"
_SA_TEMPLATE = {
    "create": True,
    "name": _SA_NAME,
    "users": {
        _SA_USERS[0]: [_SA_USER_ROLE],
        _SA_USERS[1]: [_SA_USER_ROLE],
    },
}

# Mocked user input

_YES_INPUTS = ["yes\n", "true\n", "y\n", "1\n", "\n"]
_NO_INPUTS = ["no\n", "false\n", "n\n", "0\n"]
_YES = _YES_INPUTS[0]
_NO = _NO_INPUTS[0]

_EXIT_CONDITION = "exit"
_CHOICE_1 = "str1"
_CHOICE_2 = "str2"
_INPUT_1 = f"{_CHOICE_1}\n"
_INPUT_2 = f"{_CHOICE_2}\n"
_INPUT_EXIT = f"\n{_YES}"
_CANCEL_EXIT = f"\n{_NO}"

# Mocked user input to test prompting functions

_LOOP_INPUTS = [
    f"{_INPUT_1}{_INPUT_2}{_INPUT_EXIT}",
    f"{_INPUT_1}{_CANCEL_EXIT}{_INPUT_2}{_INPUT_EXIT}",
    f"{_CANCEL_EXIT}{_INPUT_1}{_INPUT_2}{_INPUT_EXIT}",
    f"{_INPUT_1}{_INPUT_2}{_CANCEL_EXIT}{_INPUT_EXIT}",
]

_LOOP_RESULT = [_CHOICE_1, _CHOICE_2]

_NESTED_LOOP_INPUTS = [
    f"{_INPUT_1}{_INPUT_1}{_INPUT_EXIT}{_INPUT_2}{_INPUT_2}{_INPUT_EXIT}{_INPUT_EXIT}",
    f"{_INPUT_1}{_INPUT_1}{_INPUT_EXIT}{_CANCEL_EXIT}{_INPUT_2}{_INPUT_2}{_INPUT_EXIT}{_INPUT_EXIT}",
    f"{_CANCEL_EXIT}{_INPUT_1}{_INPUT_1}{_INPUT_EXIT}{_INPUT_2}{_INPUT_2}{_INPUT_EXIT}{_INPUT_EXIT}",
    f"{_INPUT_1}{_INPUT_1}{_INPUT_EXIT}{_INPUT_2}{_INPUT_2}{_INPUT_EXIT}{_CANCEL_EXIT}{_INPUT_EXIT}",
]

_NESTED_LOOP_RESULT = {_CHOICE_1: [_CHOICE_1], _CHOICE_2: [_CHOICE_2]}

# Mocked user input to test post generation hooks

_GROUP = "group"
_GROUP_NAME = f"{_GROUP}\n"
_GROUP_EMAIL = f"{_GROUP}@devoteam.com\n"
_USER = "user@devoteam.com\n"
_ROLE = "roles/viewer\n"

_BASE_HOOK_INPUTS = [
    f"{_NO}{_NO}" * 4,
    f"{_YES}{_GROUP_NAME}{_GROUP_EMAIL}{_ROLE}{_INPUT_EXIT}{_INPUT_EXIT}{_NO}" * 4,
    f"{_NO}{_YES}{_USER}{_ROLE}{_INPUT_EXIT}{_INPUT_EXIT}" * 4,
    f"{_YES}{_GROUP_NAME}{_GROUP_EMAIL}{_ROLE}{_INPUT_EXIT}{_INPUT_EXIT}{_YES}{_USER}{_ROLE}{_INPUT_EXIT}{_INPUT_EXIT}"
    * 4,
]
_POC_HOOK_INPUTS = [
    f"{_NO}{_NO}",
    f"{_YES}{_GROUP_NAME}{_GROUP_EMAIL}{_ROLE}{_INPUT_EXIT}{_INPUT_EXIT}{_NO}",
    f"{_NO}{_YES}{_USER}{_ROLE}{_INPUT_EXIT}{_INPUT_EXIT}",
    f"{_YES}{_GROUP_NAME}{_GROUP_EMAIL}{_ROLE}{_INPUT_EXIT}{_INPUT_EXIT}{_YES}{_USER}{_ROLE}{_INPUT_EXIT}{_INPUT_EXIT}",
]
_PIPELINE_HOOK_INPUTS_BASE = [
    f"{_USER}{_INPUT_EXIT}{_ROLE}{_INPUT_EXIT}" * 3
    + f"{_ROLE}{_INPUT_EXIT}\n\n\n\n\n\n",
    f"\n\n\n",
]
_PIPELINE_HOOK_INPUTS_POC = [
    f"{_USER}{_INPUT_EXIT}{_ROLE}{_INPUT_EXIT}" + f"{_ROLE}{_INPUT_EXIT}\n\n",
    f"\n\n\n",
]
_COMPONENT_HOOK_INPUTS = [
    f"{_ROLE}{_INPUT_EXIT}\n\n\n\n\n\n",
    f"\n\n\n",
]

_BASE_HOOK_TEST_REPOS = ["no_iam", "add_groups", "add_users", "add_groups_users"]

_POC_HOOK_TEST_REPOS = ["no_iam", "add_groups", "add_users", "add_groups_users"]

_PIPELINE_HOOK_TEST_REPOS = ["add_pipeline_tf", "no_iam"]

_COMPONENT_HOOK_TEST_REPOS = ["add_component_tf", "no_iam"]

_PIPELINE_HOOK_BASE_INPUTS = [_BASE_HOOK_INPUTS[0], "\n\n\n"]

_COMPONENT_HOOK_BASE_INPUTS = [_BASE_HOOK_INPUTS[0], "\n\n\n"]

_PIPELINE_HOOK_BASE_CONTEXT = [None, {"include_iam": "No"}]

_COMPONENT_HOOK_BASE_CONTEXT = [None, {"include_iam": "No"}]

_PIPELINE_HOOK_POC_INPUTS = [_POC_HOOK_INPUTS[0], "\n\n\n"]

_COMPONENT_HOOK_POC_INPUTS = [_POC_HOOK_INPUTS[0], "\n\n\n"]

_PIPELINE_HOOK_POC_CONTEXT = [None, {"include_iam": "No"}]

_COMPONENT_HOOK_POC_CONTEXT = [None, {"include_iam": "No"}]

# Mocked user input to test pre generation hooks

_PIPELINE_PRE_HOOK_CONTEXT = [
    {"pipeline_name": "pipeline"},
    {"pipeline_name": "pipeline0"},
    {"pipeline_sa": "cloudbuild"},
    {"pipeline_sa": "terraform"},
    {"pipeline_sa": "terraform_ops"},
    {"pipeline_name": "a" * 3},
    {"pipeline_name": "0pipeline"},
    {"pipeline_name": "_pipeline"},
    {"pipeline_name": "pipeline_"},
]

_PIPELINE_PRE_HOOK_SYSEXIT = [0] * 2 + [1] * 7

_COMPONENT_PRE_HOOK_CONTEXT = [
    {"image_dest": "image"},
    {"image_dest": "0image"},
    {"image_dest": "image.image"},
    {"image_dest": "image-image"},
    {"image_dest": "image_image"},
    {"image_dest": "image__image"},
    {"image_dest": "image/image"},
    {"component_name": "component"},
    {"image_dest": "_image"},
    {"image_dest": "image___image"},
    {"image_dest": "image_"},
    {"image_dest": "image/"},
    {"image_dest": "/image"},
    {"image_dest": "a" * 256},
    {"component_name": "_component"},
]

_COMPONENT_PRE_HOOK_SYSEXIT = [0] * 8 + [1] * 7


@pytest.fixture
def mocked_input(monkeypatch, request):
    """Set inputs for test_prompt_loop_exit_no."""
    monkeypatch.setattr("sys.stdin", StringIO(request.param))
