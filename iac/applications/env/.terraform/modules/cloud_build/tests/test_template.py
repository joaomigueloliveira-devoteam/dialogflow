"""Test pipeline template."""
import os
import sys
import pytest
import shutil
import subprocess
from collections import OrderedDict
from jinja2 import Template
from cookiecutter.main import cookiecutter
from cookiecutter.prompt import prompt_for_config
from cookiecutter.generate import generate_context

from user_inputs import (
    _TEMPLATES,
    _PIPELINE_PRE_HOOK_CONTEXT,
    _PIPELINE_PRE_HOOK_SYSEXIT,
    _COMPONENT_PRE_HOOK_CONTEXT,
    _COMPONENT_PRE_HOOK_SYSEXIT,
    _BASE_HOOK_TEST_REPOS,
    _POC_HOOK_TEST_REPOS,
    _PIPELINE_HOOK_TEST_REPOS,
    _COMPONENT_HOOK_TEST_REPOS,
    _BASE_HOOK_INPUTS,
    _POC_HOOK_INPUTS,
    _PIPELINE_HOOK_INPUTS_BASE,
    _PIPELINE_HOOK_INPUTS_POC,
    _PIPELINE_HOOK_BASE_INPUTS,
    _PIPELINE_HOOK_BASE_CONTEXT,
    _PIPELINE_HOOK_POC_INPUTS,
    _PIPELINE_HOOK_POC_CONTEXT,
    _COMPONENT_HOOK_INPUTS,
    _COMPONENT_HOOK_BASE_INPUTS,
    _COMPONENT_HOOK_BASE_CONTEXT,
    _COMPONENT_HOOK_POC_INPUTS,
    _COMPONENT_HOOK_POC_CONTEXT,
)


@pytest.fixture
def output_dir(tmp_path):
    """Create temporary folder to test templates."""
    path = tmp_path / "tmp_folder"
    return str(path.mkdir())


def _are_dir_equal(dir1, dir2):
    assert set(os.listdir(dir1)) == set(os.listdir(dir2))

    for path in os.listdir(dir1):
        full_path_1 = os.path.join(dir1, path)
        full_path_2 = os.path.join(dir2, path)
        if os.path.isfile(full_path_1):
            with open(full_path_1, "r") as f1:
                with open(full_path_2, "r") as f2:
                    assert f1.read() == f2.read()
        else:
            assert _are_dir_equal(full_path_1, full_path_2)
    return True


@pytest.mark.parametrize("include_iam", ["Yes", "No"])
def test_base_template(include_iam, output_dir):
    try:
        cookiecutter(
            os.getcwd(),
            no_input=True,
            output_dir=output_dir,
            accept_hooks=False,
            extra_context={"include_iam": include_iam, "template": _TEMPLATES["base"]},
        )

        assert _are_dir_equal(
            output_dir,
            os.path.join(
                os.getcwd(), "tests", "test_repo_base", "no_hooks", include_iam
            ),
        )
    except AssertionError:
        raise
    finally:
        shutil.rmtree(output_dir)


@pytest.mark.parametrize("include_iam", ["Yes", "No"])
def test_poc_template(include_iam, output_dir):
    try:
        cookiecutter(
            os.getcwd(),
            no_input=True,
            output_dir=output_dir,
            accept_hooks=False,
            extra_context={"include_iam": include_iam, "template": _TEMPLATES["poc"]},
        )

        assert _are_dir_equal(
            output_dir,
            os.path.join(
                os.getcwd(), "tests", "test_repo_poc", "no_hooks", include_iam
            ),
        )
    except AssertionError:
        raise
    finally:
        shutil.rmtree(output_dir)


def test_pipeline_template(output_dir):
    try:
        cookiecutter(
            os.getcwd(),
            no_input=True,
            output_dir=output_dir,
            accept_hooks=False,
            extra_context={"template": _TEMPLATES["pipeline"]},
        )

        assert _are_dir_equal(
            output_dir,
            os.path.join(os.getcwd(), "tests", f"test_repo_pipeline", "no_hooks"),
        )
    except AssertionError:
        raise
    finally:
        shutil.rmtree(output_dir)


@pytest.mark.parametrize("entrypoint", ["python", "bash", "other"])
def test_component_template(entrypoint, output_dir):
    try:
        cookiecutter(
            os.getcwd(),
            no_input=True,
            output_dir=output_dir,
            accept_hooks=False,
            extra_context={
                "entrypoint_format": entrypoint,
                "template": _TEMPLATES["component"],
            },
        )

        assert _are_dir_equal(
            output_dir,
            os.path.join(
                os.getcwd(), "tests", "test_repo_component", "no_hooks", entrypoint
            ),
        )
    except AssertionError:
        raise
    finally:
        shutil.rmtree(output_dir)


def _generate_hook(hook_path, context_path, output_path, extra_context=None):
    if extra_context is None:
        extra_context = dict()
    context = generate_context(
        context_file=context_path, default_context=OrderedDict([])
    )
    context["cookiecutter"] = prompt_for_config(context=context, no_input=True)
    context["cookiecutter"].update(extra_context)
    with open(hook_path, "r") as template_file:
        template = template_file.read()
    hook_file = output_path / "hook.py"
    with open(hook_file, "w") as f:
        f.write(Template(template).render(context))

    return hook_file


def _run_hook(hook, cwd, input):
    proc = subprocess.Popen(
        [sys.executable, hook],
        shell=sys.platform.startswith("win"),
        cwd=cwd,
        stdin=subprocess.PIPE,
        text=True,
    )
    proc.communicate(input=input)
    return proc.wait()


def _render_template(
    template, tmp_path, output_dir, hook_input, hook_type="pre", extra_context=None
):
    if extra_context is None:
        extra_context = {}
    extra_context["_test"] = True
    extra_context["template"] = _TEMPLATES[template]

    test_project = cookiecutter(
        os.getcwd(),
        no_input=True,
        output_dir=str(output_dir),
        accept_hooks=False,
        extra_context=extra_context,
    )

    hook_path = os.path.join(
        os.getcwd(), template, "hooks", f"{hook_type}_gen_project.py"
    )
    config_path = os.path.join(os.getcwd(), template, "cookiecutter.json")

    hook = _generate_hook(hook_path, config_path, tmp_path, extra_context)
    exit_status = _run_hook(
        hook=hook, cwd=os.path.join(output_dir, test_project), input=hook_input
    )
    return exit_status, test_project


def _test_template_hooks(
    template,
    tmp_path,
    mocked_input_base,
    hook_type="pre",
    iac_template="base",
    mocked_input_hook=None,
    test_directory=None,
    extra_context_base=None,
    extra_context_hook=None,
    sysexit=0,
):
    try:
        base_dir = tmp_path / "tmp_folder"
        base_dir.mkdir()
        base_hook_type = "post" if template != "base" else hook_type
        exit_status, project_dir = _render_template(
            template=iac_template,
            tmp_path=tmp_path,
            hook_input=mocked_input_base,
            output_dir=base_dir,
            hook_type=base_hook_type,
            extra_context=extra_context_base,
        )
        if template == "base" or template == "poc":
            assert exit_status == sysexit
        else:
            assert exit_status == 0

        if template != "base" and template != "poc":
            template_dir = (
                os.path.join(project_dir, "pipelines")
                if template == "pipeline"
                else os.path.join(project_dir, "components")
            )
            exit_status, _ = _render_template(
                template=template,
                tmp_path=tmp_path,
                hook_input=mocked_input_hook,
                output_dir=template_dir,
                hook_type=hook_type,
                extra_context=extra_context_hook,
            )
            assert exit_status == sysexit

        if hook_type == "post":
            assert _are_dir_equal(
                base_dir,
                os.path.join(
                    os.getcwd(),
                    "tests",
                    f"test_repo_{template}",
                    "hooks",
                    test_directory,
                ),
            )

    except AssertionError:
        raise
    finally:
        shutil.rmtree(base_dir)


def _test_template_pre_hooks(
    template,
    tmp_path,
    mocked_input_base,
    extra_context_base=None,
    extra_context_hook=None,
    sysexit=0,
):
    _test_template_hooks(
        template=template,
        tmp_path=tmp_path,
        mocked_input_base=mocked_input_base,
        hook_type="pre",
        extra_context_base=extra_context_base,
        extra_context_hook=extra_context_hook,
        sysexit=sysexit,
    )


def _test_template_post_hooks(
    template,
    tmp_path,
    test_directory,
    mocked_input_base,
    iac_template="base",
    mocked_input_hook=None,
    extra_context_base=None,
    extra_context_hook=None,
):
    _test_template_hooks(
        template=template,
        tmp_path=tmp_path,
        mocked_input_base=mocked_input_base,
        mocked_input_hook=mocked_input_hook,
        hook_type="post",
        test_directory=test_directory,
        iac_template=iac_template,
        extra_context_base=extra_context_base,
        extra_context_hook=extra_context_hook,
    )


@pytest.mark.parametrize(
    "extra_context_hook, expected_sysexit",
    zip(_PIPELINE_PRE_HOOK_CONTEXT, _PIPELINE_PRE_HOOK_SYSEXIT),
)
def test_pipeline_template_pre_hooks(tmp_path, extra_context_hook, expected_sysexit):
    _test_template_pre_hooks(
        template="pipeline",
        tmp_path=tmp_path,
        mocked_input_base=_BASE_HOOK_INPUTS[0],
        extra_context_hook=extra_context_hook,
        sysexit=expected_sysexit,
    )


@pytest.mark.parametrize(
    "extra_context_hook, expected_sysexit",
    zip(_COMPONENT_PRE_HOOK_CONTEXT, _COMPONENT_PRE_HOOK_SYSEXIT),
)
def test_component_template_pre_hooks(tmp_path, extra_context_hook, expected_sysexit):
    _test_template_pre_hooks(
        template="component",
        tmp_path=tmp_path,
        mocked_input_base=_BASE_HOOK_INPUTS[0],
        extra_context_hook=extra_context_hook,
        sysexit=expected_sysexit,
    )


@pytest.mark.parametrize(
    "directory, mocked_input",
    zip(_BASE_HOOK_TEST_REPOS, _BASE_HOOK_INPUTS),
)
def test_base_template_post_hooks(directory, tmp_path, mocked_input):
    _test_template_post_hooks(
        template="base",
        tmp_path=tmp_path,
        mocked_input_base=mocked_input,
        test_directory=directory,
    )


@pytest.mark.parametrize(
    "directory, mocked_input",
    zip(_POC_HOOK_TEST_REPOS, _POC_HOOK_INPUTS),
)
def test_poc_template_post_hooks(directory, tmp_path, mocked_input):
    _test_template_post_hooks(
        template="poc",
        tmp_path=tmp_path,
        iac_template="poc",
        mocked_input_base=mocked_input,
        test_directory=directory,
    )


@pytest.mark.parametrize(
    "directory, mocked_input, extra_context_base, mocked_input_base",
    zip(
        _PIPELINE_HOOK_TEST_REPOS,
        _PIPELINE_HOOK_INPUTS_BASE,
        _PIPELINE_HOOK_BASE_CONTEXT,
        _PIPELINE_HOOK_BASE_INPUTS,
    ),
)
def test_pipeline_base_template_post_hooks(
    directory, tmp_path, mocked_input, extra_context_base, mocked_input_base
):
    _test_template_post_hooks(
        template="pipeline",
        tmp_path=tmp_path,
        extra_context_base=extra_context_base,
        mocked_input_base=mocked_input_base,
        mocked_input_hook=mocked_input,
        test_directory=os.path.join("base", directory),
    )


@pytest.mark.parametrize(
    "directory, mocked_input, extra_context_base, mocked_input_base",
    zip(
        _PIPELINE_HOOK_TEST_REPOS,
        _PIPELINE_HOOK_INPUTS_POC,
        _PIPELINE_HOOK_POC_CONTEXT,
        _PIPELINE_HOOK_POC_INPUTS,
    ),
)
def test_pipeline_poc_template_post_hooks(
    directory, tmp_path, mocked_input, extra_context_base, mocked_input_base
):
    _test_template_post_hooks(
        template="pipeline",
        tmp_path=tmp_path,
        iac_template="poc",
        extra_context_base=extra_context_base,
        mocked_input_base=mocked_input_base,
        mocked_input_hook=mocked_input,
        test_directory=os.path.join("poc", directory),
    )


@pytest.mark.parametrize(
    "directory, mocked_input, extra_context_base, mocked_input_base",
    zip(
        _COMPONENT_HOOK_TEST_REPOS,
        _COMPONENT_HOOK_INPUTS,
        _COMPONENT_HOOK_BASE_CONTEXT,
        _COMPONENT_HOOK_BASE_INPUTS,
    ),
)
def test_component_base_template_post_hooks(
    directory, tmp_path, mocked_input, extra_context_base, mocked_input_base
):
    _test_template_post_hooks(
        template="component",
        tmp_path=tmp_path,
        extra_context_base=extra_context_base,
        mocked_input_base=mocked_input_base,
        mocked_input_hook=mocked_input,
        test_directory=os.path.join("base", directory),
    )


@pytest.mark.parametrize(
    "directory, mocked_input, extra_context_base, mocked_input_base",
    zip(
        _COMPONENT_HOOK_TEST_REPOS,
        _COMPONENT_HOOK_INPUTS,
        _COMPONENT_HOOK_POC_CONTEXT,
        _COMPONENT_HOOK_POC_INPUTS,
    ),
)
def test_component_poc_template_post_hooks(
    directory, tmp_path, mocked_input, extra_context_base, mocked_input_base
):
    _test_template_post_hooks(
        template="component",
        tmp_path=tmp_path,
        iac_template="poc",
        extra_context_base=extra_context_base,
        mocked_input_base=mocked_input_base,
        mocked_input_hook=mocked_input,
        test_directory=os.path.join("poc", directory),
    )
