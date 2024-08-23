"""Installation file for cookiecutter_utils."""
from setuptools import find_packages
from setuptools import setup

setup(
    name="cookiecutter_utils",
    description="Utility functions for cookiecutter templates",
    author="Devoteam G Cloud",
    version="0.0.1",
    python_requires=">=3.7",
    packages=find_packages(),
    include_package_data=True,
)
