"""Test functions in cookiecutter_utils/gcp_templates.py."""

from cookiecutter_utils import gcp_templates

from user_inputs import (
    _TRIGGER_INCLUDED,
    _TRIGGER_PATH,
    _TRIGGER_SUBSTITUTIONS,
    _TRIGGER_BRANCH_REGEX,
    _TRIGGER_TEMPLATE,
    _BUCKET_NAME,
    _BUCKET_REGION,
    _BUCKET_TEMPLATE,
    _SA_NAME,
    _SA_USERS,
    _SA_TEMPLATE,
)


def test_cloudbuild_trigger_template():
    """Test cloudbuild_trigger_template."""

    test_template = gcp_templates.cloudbuild_trigger_template(
        included=_TRIGGER_INCLUDED,
        path=_TRIGGER_PATH,
        substitutions=_TRIGGER_SUBSTITUTIONS,
        branch_regex=_TRIGGER_BRANCH_REGEX,
    )
    assert test_template == _TRIGGER_TEMPLATE


def test_gcs_bucket_template():
    """Test gcs_bucket_template."""

    test_template = gcp_templates.gcs_bucket_template(
        name=_BUCKET_NAME, region=_BUCKET_REGION
    )
    assert test_template == _BUCKET_TEMPLATE


def test_service_account_template():
    """Test service_account_template."""

    test_template = gcp_templates.service_account_template(
        name=_SA_NAME, users=_SA_USERS
    )
    assert test_template == _SA_TEMPLATE
