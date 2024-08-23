"""Check if component name is valid."""

import re
import sys

_VALID_AR_COMPONENT_PATTERN = re.compile(
    "^([a-z0-9]([a-z0-9]|([.][a-z0-9])|(-[a-z0-9])|(__?[a-z0-9]))*/)*([a-z0-9]([a-z0-9]|([.][a-z0-9])|(-[a-z0-9])|(__?[a-z0-9]))*)$"
)

if len("{{cookiecutter['image_dest']}}") > 255:
    print("Docker image names should not be longer than 255 characters.")

    sys.exit(1)

if not re.match(
    _VALID_AR_COMPONENT_PATTERN, "{{cookiecutter['image_dest']}}"
):
    if (
        "${_ARTIFACT_REGISTRY_CONTAINERS_URL}"
        in "{{cookiecutter['image_dest']}}"
    ):
        if not re.match(
            _VALID_AR_COMPONENT_PATTERN, "{{cookiecutter['component_name']}}"
        ):
            print(
                "ERROR: {{cookiecutter['image_dest']}} is not a valid docker image name."
            )

            sys.exit(1)
    else:
        sys.exit(1)
