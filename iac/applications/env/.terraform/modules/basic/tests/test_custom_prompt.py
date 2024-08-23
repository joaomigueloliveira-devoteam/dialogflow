"""Test functions in cookiecutter_utils/gcp_templates.py."""
import pytest
from cookiecutter_utils import custom_prompt

from user_inputs import (
    mocked_input,
    _EXIT_CONDITION,
    _LOOP_INPUTS,
    _LOOP_RESULT,
    _NESTED_LOOP_INPUTS,
    _NESTED_LOOP_RESULT,
    _YES_INPUTS,
    _NO_INPUTS,
)


@pytest.mark.parametrize("mocked_input", _LOOP_INPUTS, indirect=True)
def test_read_user_variable_list(mocked_input):
    """Test read_user_variable_list."""
    test_variables = custom_prompt.read_user_variable_list(
        var_name="name", exit_condition=_EXIT_CONDITION
    )

    assert test_variables == _LOOP_RESULT


@pytest.mark.parametrize("mocked_input", _NESTED_LOOP_INPUTS, indirect=True)
def test_read_user_variable_json(mocked_input):
    """Test read_user_variable_json."""
    test_variables = custom_prompt.read_user_variable_json(
        var_name="name",
        exit_condition=_EXIT_CONDITION,
        inner_func=custom_prompt.read_user_variable_list,
        inner_func_args={"var_name": "var", "exit_condition": _EXIT_CONDITION},
    )

    assert test_variables == _NESTED_LOOP_RESULT


@pytest.mark.parametrize("mocked_input", _YES_INPUTS, indirect=True)
def test_prompt_loop_exit_yes(mocked_input):
    """Test prompt_loop_exit with positive answer."""
    loop = custom_prompt.prompt_loop_exit()
    assert loop == False


@pytest.mark.parametrize("mocked_input", _NO_INPUTS, indirect=True)
def test_prompt_loop_exit_no(mocked_input):
    """Test prompt_loop_exit with negative answer."""
    loop = custom_prompt.prompt_loop_exit()
    assert loop == True
