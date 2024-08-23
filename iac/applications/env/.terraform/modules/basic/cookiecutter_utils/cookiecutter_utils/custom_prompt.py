"""Custom prompt functions for cookiecutter templates."""

from cookiecutter import prompt
from typing import Callable, Dict, Any


def read_user_variable_json(
    var_name: str,
    exit_condition: str,
    prefix: str = "",
    inner_func: Callable = None,
    inner_func_args: Dict[str, Any] = [],
):
    """
    Prompt user for multiple elements and return as dict.

    :param var_name: name of dict variable
    :param exit_condition: input string to stop the loop
    :param inner_func: function to call during loop
    :param inner_func_args: arguments of inner function
    :return: dict of strings to empty dict or inner func result
    """
    variables = dict()
    loop = True

    while loop:
        var = prompt.read_user_variable(
            var_name=var_name, default_value=exit_condition, prefix=prefix
        )
        if var != exit_condition:
            variables[var] = dict()
            if inner_func is not None:
                variables[var] = inner_func(prefix=prefix, **inner_func_args)
        else:
            loop = prompt_loop_exit(prefix=prefix)

    return variables


def read_user_variable_list(var_name: str, exit_condition: str, prefix: str = ""):
    """
    Prompt user for multiple elements and return as list.

    :param var_name: name of dict variable
    :param exit_condition: input string to stop the loop
    :return: list of strings
    """
    return list(read_user_variable_json(var_name, exit_condition, prefix).keys())


def prompt_loop_exit(prefix: str = ""):
    """
    Prompts the user for input to exit a loop.

    :return: True to continue looping, False to stop loop
    """
    stop_loop = prompt.read_user_yes_no(
        var_name="Exit?", default_value="Yes", prefix=prefix
    )
    return not stop_loop
