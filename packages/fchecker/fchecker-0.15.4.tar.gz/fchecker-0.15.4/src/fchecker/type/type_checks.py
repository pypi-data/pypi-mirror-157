# Built-in/Generic Imports
from typing import Union, Optional, Any

# Exceptions
from fexception import FAttributeError, FTypeError

__author__ = "IncognitoCoding"
__copyright__ = "Copyright 2022, type_check"
__credits__ = ["IncognitoCoding"]
__license__ = "MIT"
__version__ = "0.0.10"
__maintainer__ = "IncognitoCoding"
__status__ = "Beta"


def type_check(
    value: Any,
    required_type: Union[type, tuple[type, ...]],
    enforce: bool = True,
    tb_remove_name: Optional[str] = None,
    msg_override: Optional[str] = None,
) -> Union[FTypeError, bool]:
    """
    A simple type validation check. This function is designed to be widely used to check any values.

    Raises a cleanly formatted reason if the type validation is unsuccessful.

    A None value will return different exceptions based on msg_override.\\
    \t\\- No msg_override = FAttributeError\\
    \t\\- msg_override = FTypeError

    Calling Examples:
    \t\\- type_check('sample', (int, str))\\
    \t\\- type_check('sample', str)

    NOTE:
    \t\\- Pylance type detection does not work through type_checks.\\
    \t\t\\- It would be best if you used isinstance for Pylance type checking.

    Args:
        value (any):
        \t\\- Any value needing its type validated.\\
        required_type (Union[type, tuple[type, ...]]):
        \t\\- The required type the value should match.\\
        \t\\- Can be a single type or typle of types.
        enforce (bool, optional):
        \t\\- A failed match will return a raised FTypeError exception.\\
        \t\\- Defaults to True.
        tb_remove_name (str, optional):\\
        \t\\- Caller function name or any other function in the\\
        \t   traceback chain.\\
        \t\\- Removes all traceback before and at this function.\\
        \t\\- Defaults to None.
        msg_override (str, optional):
        \t\\- Main top-level message override.\\
        \t\\- The expected and returned results will be the same.\\
        \t\\- Ideal for type checks for other importing files such as YAML.\\
        \t\\- Defaults to None.

    Raises:
        FAttributeError (fexception):
        \t\\- The value \'{value}\' sent is not an accepted input.
        FTypeError (fexception):
        \t\\- A user defined msg_override message.
        FAttributeError (fexception):
        \t\\- No type or list of types has been entered for type validation.
        FAttributeError (fexception):
        \t\\- The enforce argument value is not the correct type.
        FTypeError (fexception):
        \t\\- The value \'{value}\' is not in {required_type} format.
    
    Returns:
        Union[FTypeError, bool]:
        \t\\- FTypeError:\\
        \t\t\\- Returns raised formatted exception of the type check match fails\\
        \t\t   when 'enforce' is set to True.\\
        \t\\- bool:
        \t\t\\- Returns True if the type matches.\\
        \t\t\\- False will return when 'enforce' is set to False.
    """
    # Verifies a value is sent.
    if value is None or value == "":
        # Sets message override if one is provided.
        if msg_override:
            exc_args: dict = {
                "main_message": msg_override,
                "expected_result": "Any value other than None or an empty string",
                "returned_result": type(value),
            }
            if not tb_remove_name:
                tb_remove_name = "type_check"
            raise FTypeError(message_args=exc_args, tb_limit=None, tb_remove_name=tb_remove_name)
        else:
            exc_args: dict = {
                "main_message": f"The value '{value}' sent is not an accepted input.",
                "expected_result": "Any value other than None or an empty string",
                "returned_result": type(value),
            }
            if not tb_remove_name:
                tb_remove_name = "type_check"
            raise FAttributeError(message_args=exc_args, tb_limit=None, tb_remove_name=tb_remove_name)

    # Verifies a type or tuple is sent.
    if not (isinstance(required_type, type) or isinstance(required_type, tuple)):
        exc_args: dict = {
            "main_message": "No type or tuple of types has been entered for type validation.",
            "expected_result": "type or typle of types",
            "returned_result": type(required_type),
        }
        if not tb_remove_name:
            tb_remove_name = "type_check"
        raise FAttributeError(message_args=exc_args, tb_limit=None, tb_remove_name=tb_remove_name)

    # Verifies a bool is sent.
    if not isinstance(enforce, bool):
        exc_args: dict = {
            "main_message": "The enforce argument value is not the correct type.",
            "expected_result": "<class 'bool'>",
            "returned_result": type(enforce),
        }
        if not tb_remove_name:
            tb_remove_name = "type_check"
        raise FAttributeError(message_args=exc_args, tb_limit=None, tb_remove_name=tb_remove_name)

    matching_type_flag: bool = False
    if isinstance(value, required_type):
        # Bool is a subclass of int.
        # This forces the variable bool to match the bool and not an integer.
        if "<class 'bool'>" == str(type(value)):
            if "<class 'bool'>" in str(required_type):
                matching_type_flag = True
            else:
                matching_type_flag = False
        else:
            matching_type_flag = True
    else:
        # Gives the option to return standard bool or an exception.
        if enforce:
            matching_type_flag = False
        else:
            return False

    # Checks for no match.
    if matching_type_flag is False:
        adjusted_required_type: Union[str, type]
        # Converts the list to a string with an '|' value between each type.
        if isinstance(required_type, tuple):
            adjusted_required_type = " | ".join(map(str, required_type))
        else:
            adjusted_required_type = required_type

        # Sets message override if one is provided.
        if msg_override:
            main_message: str = msg_override
        else:
            main_message: str = (
                f"The object value '{value}' is not an instance of the required class(es) or subclass(es)."
            )

        exc_args: dict = {
            "main_message": main_message,
            "expected_result": adjusted_required_type,
            "returned_result": type(value),
        }
        if not tb_remove_name:
            tb_remove_name = "type_check"
        raise FTypeError(message_args=exc_args, tb_limit=None, tb_remove_name=tb_remove_name)
    else:
        return True
