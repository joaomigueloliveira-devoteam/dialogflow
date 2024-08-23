"""Terraform templates for GCP resources to add in cookiecutter hooks."""

from typing import List, Dict

_DEFAULT_PIPELINE_SA_ROLES = [
    "roles/aiplatform.admin",
    "roles/aiplatform.customCodeServiceAgent",
    "roles/aiplatform.serviceAgent",
    "roles/artifactregistry.reader",
    "roles/bigquery.dataOwner",
    "roles/datastore.user",
    "roles/ml.developer",
    "roles/ml.serviceAgent",
    "roles/storage.admin",
]

_DEFAULT_CLOUDBUILD_SA_ROLES = [
    "roles/artifactregistry.reader",
    "roles/iam.serviceAccountUser",
    "roles/aiplatform.user",
]


def cloudbuild_trigger_template(
    included: List[str],
    path: str,
    substitutions: Dict[str, str],
    branch_regex: str,
):
    """
    Template for Cloud Build trigger in Terraform.

    :param included: files included in trigger
    :param path: path to cloudbuild.yaml
    :param substitutions: substitutions to apply during build
    :param branch_regex: branch to fire the trigger
    :return: json trigger
    """
    template = {
        "included": included,
        "path": path,
        "substitutions": substitutions,
        "branch_regex": branch_regex,
    }
    return template


def gcs_bucket_template(
    name: str,
    region: str,
):
    """
    Template for GCS bucket in Terraform.

    :param name: bucket name
    :param region: bucket region
    :return: json bucket
    """
    template = {
        "name": name,
        "region": region,
    }
    return template


def service_account_template(
    name: str,
    users: List[str],
):
    """
    Template for new service account in Terraform.

    :param name: SA name
    :param users: SA users
    :return: json SA
    """
    template = {
        "create": True,
        "name": name,
        "users": dict(
            zip(
                users,
                [["roles/iam.serviceAccountUser"] for _ in users],
            )
        ),
    }
    return template
