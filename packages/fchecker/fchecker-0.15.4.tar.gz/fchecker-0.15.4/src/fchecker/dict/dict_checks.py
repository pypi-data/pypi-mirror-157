# Built-in/Generic Imports
from typing import Union, Any

# Local Functions
from ..type.type_checks import type_check

# Local Exceptions
from ..exceptions.exceptions import InvalidKeyError

# Exceptions
from fexception import FCustomException, FAttributeError

__author__ = "IncognitoCoding"
__copyright__ = "Copyright 2022, KeyCheck"
__credits__ = ["IncognitoCoding"]
__license__ = "MIT"
__version__ = "0.0.9"
__maintainer__ = "IncognitoCoding"
__status__ = "Beta"


class KeyCheck:
    """
    An advanced dictionary key checker that offers two different check options.

    Raises a cleanly formatted reason if the key validation is unsuccessful.

    No return output.

    Options:\\
    \t\\- contains_keys():\\
    \t\t\\- Checks if some required keys exist in the dictionary.\\
    \t\\- all_keys():\\
    \t\t\\- Checks if all required keys exist in the dictionary.

    Args:
        values (dict):\\
        \t\\- A dictionary that needs the keys validated.
        \t\t\\- A template can be used with the reverse option enabled.
        enforce (bool, optional):
        \t\\- A failed match will return a raised FTypeError exception.\\
        \t\\- Defaults to True.
    
    Raises:
        FTypeError (fexception):
        \t\\- The object value '{values}' is not an instance of the required class(es) or subclass(es).
        FTypeError (fexception):
        \t\\- The object value '{enforce}' is not an instance of the required class(es) or subclass(es).
    """

    def __init__(
        self, values: dict[Union[int, float, bool, str, tuple[Union[int, float, bool, str]]], Any], enforce: bool = True
    ) -> None:
        type_check(value=values, required_type=dict, tb_remove_name="__init__")
        type_check(value=enforce, required_type=bool, tb_remove_name="__init__")

        self.__values: dict = values
        self.__required_keys: Union[Any, tuple[Any, ...]] = ""
        self.__enforce: bool = enforce

    def contains_keys(
        self,
        required_keys: Union[
            int,
            float,
            bool,
            str,
            tuple[Union[int, float, bool, str]],
            tuple[Union[int, float, bool, str, tuple[Union[int, float, bool, str]]], ...],
        ],
        reverse_output: bool = False,
    ) -> Union[InvalidKeyError, bool]:
        """
        Checks if some required keys exist in the dictionary.

        Args:
            required_keys (Union[int, float, bool, str, tuple[Union[int, float, bool, str]],\\
            \t\t\t\t   tuple[Union[int, float, bool, str, tuple[Union[int, float,\\
            \t\t\t\t\t\t\t\t\t\t\t\t\t bool, str]]], ...]):\\
            \t\\- The required key(s) that should match.\\
            \t\\- Can be a single str or tuple of keys.
            reverse (bool, optional):\\
            \t\\- Reverses the key check exception output, so the\\
            \t   expected result and returned results are flipped.\\
            \t\\- Defaults to False.

        Raises:
            FTypeError (fexception):
            \t\\- The required dictionary key(s) (required_keys) must be immutable data types.
            FTypeError (fexception):
            \t\\- The object value '{reverse_output}' is not an instance of the required class(es) or subclass(es).

        Nested Raises:
            FAttributeError (fexception):\\
            \t\\- No key(s) were sent.
            FAttributeError (fexception):\\
            \t\\- The input keys have inconsistent value and requirement keys.\\
            FAttributeError (fexception):\\
            \t\\- The required key tuple contains duplicate keys. All keys must be unique.\\
            InvalidKeyError (fexception):\\
            \t\\- The dictionary key (\'{non_matching_key}\')\\
            \t  does not exist in the expected required key(s).
        
        Returns:
            Union[InvalidKeyError, bool]:
            \t\\- InvalidKeyError:\\
            \t\t\\- Returns raised formatted exception of the type check match fails\\
            \t\t   when 'enforce' is set to True.\\
            \t\\- bool:
            \t\t\\- Returns True if the type matches.\\
            \t\t\\- False will return when 'enforce' is set to False.
        """
        type_check(
            value=required_keys,
            required_type=(int, float, bool, str, tuple),
            tb_remove_name="contains_keys",
            msg_override="The required dictionary key(s) (required_keys) must be immutable data types.",
        )
        type_check(value=reverse_output, required_type=bool, tb_remove_name="contains_keys")

        self.__required_keys = required_keys
        self.__all_key_check: bool = False
        self.__reverse_output: bool = reverse_output

        return self.__key_validation()

    def all_keys(
        self,
        required_keys: Union[
            int,
            float,
            bool,
            str,
            tuple[Union[int, float, bool, str]],
            tuple[Union[int, float, bool, str, tuple[Union[int, float, bool, str]]], ...],
        ],
        reverse_output: bool = False,
    ) -> Union[InvalidKeyError, bool]:
        """
        Checks if all required keys exist in the dictionary

        Args:
            required_keys (Union[int, float, bool, str, tuple[Union[int, float, bool, str]],\\
            \t\t\t\t   tuple[Union[int, float, bool, str, tuple[Union[int, float,\\
            \t\t\t\t\t\t\t\t\t\t\t\t\t bool, str]]], ...]):\\
            \t\\- The required key(s) that should match.\\
            \t\\- Can be a single str or tuple of keys.
            reverse (bool, optional):\\
            \t\\- Reverses the key check exception output, so the\\
            \t   expected result and returned results are flipped.\\
            \t\\- Defaults to False.

        Raises:
            FTypeError (fexception):
            \t\\- The required dictionary key(s) (required_keys) must be immutable data types.
            FTypeError (fexception):
            \t\\- The object value '{reverse_output}' is not an instance of the required class(es) or subclass(es).

        Nested Raises:
            FAttributeError (fexception):\\
            \t\\- No key(s) were sent.
            FAttributeError (fexception):\\
            \t\\- The input keys have inconsistent value and requirement keys.\\
            FAttributeError (fexception):\\
            \t\\- The required key tuple contains duplicate keys. All keys must be unique.\\
            InvalidKeyError (fexception):\\
            \t\\- The dictionary key (\'{non_matching_key}\')\\
            \t  does not exist in the expected required key(s).
        
        Returns:
            Union[InvalidKeyError, bool]:
            \t\\- InvalidKeyError:\\
            \t\t\\- Returns raised formatted exception of the type check match fails\\
            \t\t   when 'enforce' is set to True.\\
            \t\\- bool:
            \t\t\\- Returns True if the type matches.\\
            \t\t\\- False will return when 'enforce' is set to False.
        """
        type_check(
            value=required_keys,
            required_type=(int, float, bool, str, tuple),
            tb_remove_name="all_keys",
            msg_override="The required dictionary key(s) (required_keys) must be immutable data types.",
        )
        if reverse_output:
            type_check(value=reverse_output, required_type=bool, tb_remove_name="all_keys")

        self.__required_keys = required_keys
        self.__all_key_check: bool = True
        self.__reverse_output: bool = reverse_output

        return self.__key_validation()

    def __key_validation(self) -> Union[InvalidKeyError, bool]:
        """
        Performs the key validation.

        Raises:
            FAttributeError (fexception):\\
            \t\\- No key(s) were sent.
            FAttributeError (fexception):\\
            \t\\- The input keys have inconsistent value and requirement keys.\\
            FAttributeError (fexception):\\
            \t\\- The required key tuple contains duplicate keys. All keys must be unique.\\
            InvalidKeyError (fexception):\\
            \t\\- The dictionary key (\'{non_matching_key}\')\\
            \t  does not exist in the expected required key(s).
        
        Returns:
            Union[InvalidKeyError, bool]:
            \t\\- InvalidKeyError:\\
            \t\t\\- Returns raised formatted exception of the file is not found.\\
            \t\\- bool:
            \t\t\\- Returns True if the key(s) are valid.\\
            \t\t\\- No False bool will return. This is replaced by the raised exception.
        """
        # Loops through to find any keys that do not match.
        dict_keys = tuple(self.__values.keys())

        # Reverses key results for flipped reverse checks.
        required_key_result: Union[Any, tuple]
        expected_key_result: Union[Any, tuple]
        if self.__reverse_output:
            expected_key_result = dict_keys
            required_key_result = self.__required_keys
        else:
            expected_key_result = self.__required_keys
            required_key_result = dict_keys

        # Checks for the required keys are sent.
        if not self.__required_keys:
            # Formats the output based on the check option.
            if self.__all_key_check:
                expected_result: str = f"  - Expected Key(s) = {expected_key_result}"
            else:
                expected_result: str = f"  - Expected Match Option Key(s) = {dict_keys}"

            exc_args = {
                "main_message": "No key(s) were sent.",
                "expected_result": expected_result,
                "returned_result": None,
            }
            if self.__all_key_check is True:
                raise FAttributeError(message_args=exc_args, tb_limit=None, tb_remove_name="all_keys")
            else:
                raise FAttributeError(message_args=exc_args, tb_limit=None, tb_remove_name="contains_keys")

        # Checks for 1:1 input when using the all_keys option.
        mismatched_input: bool = False
        if self.__all_key_check:
            mismatched_input: bool
            if isinstance(self.__required_keys, tuple):
                if len(dict_keys) != len(self.__required_keys):
                    mismatched_input = True
                else:
                    mismatched_input = False
            else:
                if len(self.__values) > 1:
                    mismatched_input = True

            if mismatched_input is True:
                exc_args: dict = {
                    "main_message": "The input keys have inconsistent value and requirement keys.",
                    "expected_result": f"Required Key(s) = {expected_key_result}",
                    "returned_result": f"Failed Key(s) = {required_key_result}",
                }
                raise FAttributeError(message_args=exc_args, tb_limit=None, tb_remove_name="all_keys")

        # Checks for duplicate values.
        if isinstance(self.__required_keys, tuple):
            if len(self.__required_keys) != len(set(self.__required_keys)):
                exc_args: dict = {
                    "main_message": "The required key tuple contains duplicate keys. All keys must be unique.",
                    "returned_result": f"Required Key(s) = {self.__required_keys}",
                }
                if self.__all_key_check is True:
                    raise FAttributeError(message_args=exc_args, tb_limit=None, tb_remove_name="all_keys")
                else:
                    raise FAttributeError(message_args=exc_args, tb_limit=None, tb_remove_name="contains_keys")

        # Sets the keys in reverse order so the no-match is the last entry checked
        # but the first no-match in the tuple of keys.
        sorted_dict_keys = sorted(dict_keys, reverse=True)

        non_matching_key: Union[Any, None] = None
        if isinstance(self.__required_keys, tuple):
            for required_key in self.__required_keys:
                # Checks if the validation requires all the required keys
                # to match all sorted_dict_keys or the required keys to match
                # some of the sorted_dict_keys.
                if self.__all_key_check:
                    for dict_key in sorted_dict_keys:
                        # Checks for exact match.
                        if required_key == dict_key:
                            non_matching_key = None
                            break
                        else:
                            non_matching_key = required_key
                else:
                    if required_key in sorted_dict_keys:
                        non_matching_key = None
                    else:
                        non_matching_key = required_key
                # If a match is not found on the first required
                # key check the loop will exit and return the no-matched key.
                if non_matching_key:
                    break
        else:
            # Variable name swap for easier loop reading.
            required_key: str = self.__required_keys
            for dict_key in sorted_dict_keys:
                if required_key == dict_key:
                    # Checks for exact match.
                    non_matching_key = None
                    break
                else:
                    non_matching_key = required_key

        # Checks if a no matching key exists, to output the error
        if non_matching_key and not self.__enforce:
            return False
        elif non_matching_key and self.__enforce:
            # Formats the output based on the check option.
            if self.__all_key_check:
                main_message: str = (
                    f"The dictionary key ('{non_matching_key}') " "does not exist in the expected required key(s).\n"
                )
                expected_result: str = f"Expected Key(s) = {expected_key_result}"
                returned_result: str = f"Failed Key(s) = {required_key_result}"
            else:
                main_message: str = (
                    f"The dictionary key ('{non_matching_key}') " "does not match any expected match option key(s).\n"
                )
                if isinstance(expected_key_result, tuple):
                    expected_result: str = f"Match Option Key(s) = {expected_key_result}"
                else:
                    expected_result: str = f"Match Option Key(s) = '{expected_key_result}'"
                returned_result: str = f"Failed Key(s) = {required_key_result}"

            exc_args: dict = {
                "main_message": main_message,
                "custom_type": InvalidKeyError,
                "expected_result": expected_result,
                "returned_result": returned_result,
            }
            if self.__all_key_check is True:
                raise InvalidKeyError(FCustomException(message_args=exc_args, tb_limit=None, tb_remove_name="all_keys"))
            else:
                raise InvalidKeyError(
                    FCustomException(message_args=exc_args, tb_limit=None, tb_remove_name="contains_keys")
                )
        else:
            return True
