"""Pipeline definition."""
import argparse

from kfp.registry import RegistryClient
from kfp import compiler, dsl

parser = argparse.ArgumentParser()
parser.add_argument(
    "--project",
    help="the project ID",
    type=str,
)
parser.add_argument(
    "--region",
    help="the region where the pipeline will be stored",
    type=str,
)
parser.add_argument(
    "--pipeline-name",
    help="the name of the pipeline",
    type=str,
    default="{{cookiecutter['pipeline_name']}}",
)
parser.add_argument(
    "--pipeline-file",
    help="the location to write the pipeline JSON to",
    type=str,
    default="pipeline.yaml",
)
parser.add_argument(
    "--artifact-registry-url",
    help="the Artifact Registry URL to save the pipeline template to",
    type=str,
)
parser.add_argument(
    "-t",
    "--tags",
    nargs="*",
    help="Extra tags to set on the image.",
    default=["latest"],
)
args = parser.parse_args()


@dsl.pipeline(name=args.pipeline_name)
def pipeline():
    pass


compiler.Compiler().compile(
    pipeline_func=pipeline,
    package_path=args.pipeline_file,
)

client = RegistryClient(host=args.artifact_registry_url)
templateName, versionName = client.upload_pipeline(
    file_name=args.pipeline_file,
    tags=args.tags,
    extra_headers={"description": "{{cookiecutter['pipeline_description']}}"},
)
