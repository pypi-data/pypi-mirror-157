from typing import List, cast, Type, Any, Union, Callable
from dataclasses import dataclass


@dataclass
class Validator:
    name: str
    value: Any
    validator: Union[Type, Callable, List[Type]]


class ValidationResult:
    def __init__(self, result: bool, message: str = None):
        self.result = result
        self.message = message

    def __bool__(self):
        return self.result


def are_valid_args(args: Union[List[Validator], Validator]) -> ValidationResult:
    if not isinstance(args, list):
        args = [args]

    if len(args) == 0:
        return ValidationResult(True)

    for arg in args:
        if not isinstance(arg, Validator):
            raise ValueError('Invalid argument to check: Must be of type Validator.')

        if type(arg.validator).__name__ == 'function':
            try:
                res = arg.validator(arg.value)

                if not isinstance(res, bool):
                    raise ValueError(
                        f'Validation function must return a bool. Validation function for {res} returned type {type(res)}')

                if not res:
                    return ValidationResult(res, f'Argument {arg.name} failed the validation function.')

                continue
            except Exception as e:
                return ValidationResult(False,
                                        f'An exception occurred in the validation function for arg {arg.name}: {str(e)}')

        else:
            types = arg.validator
            if not isinstance(types, list):
                types = [types]

            types = cast(List[Type], types)

            found = False
            for t in types:
                if t.__dict__.get('__args__'):
                    raise ValueError('Cannot use parameterized types for argument checking.')

                if isinstance(arg.value, t):
                    found = True
            if not found:
                return ValidationResult(False, f'Argument {arg.name} was of invalid type.')

    return ValidationResult(True)
