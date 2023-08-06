from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar, Union

import pydantic
from pydantic.generics import GenericModel
from typing_extensions import Literal

from classiq_interface.generator.arith.arithmetic import DEFAULT_OUT_NAME
from classiq_interface.generator.arith.fix_point_number import FixPointNumber
from classiq_interface.generator.arith.register_user_input import RegisterUserInput
from classiq_interface.generator.function_params import FunctionParams

DEFAULT_RIGHT_ARG_NAME = "right_arg"
DEFAULT_LEFT_ARG_NAME = "left_arg"
DEFAULT_GARBAGE_OUT_NAME = "deleted_qubits"
LeftDataT = TypeVar("LeftDataT")
RightDataT = TypeVar("RightDataT")
Numeric = (float, int)


class BinaryOpParams(GenericModel, FunctionParams, Generic[LeftDataT, RightDataT]):
    left_arg: LeftDataT
    right_arg: RightDataT
    output_size: Optional[pydantic.PositiveInt]
    output_name: str = DEFAULT_OUT_NAME

    @pydantic.validator("left_arg")
    def set_left_arg_name(cls, left_arg):
        if isinstance(left_arg, RegisterUserInput) and left_arg.name is None:
            left_arg.name = DEFAULT_LEFT_ARG_NAME
        return left_arg

    @pydantic.validator("right_arg")
    def set_right_arg_name(cls, right_arg):
        if isinstance(right_arg, RegisterUserInput) and right_arg.name is None:
            right_arg.name = DEFAULT_RIGHT_ARG_NAME
        return right_arg

    @pydantic.root_validator()
    def validate_one_is_register(cls, values):
        if isinstance(values.get("left_arg"), Numeric) and isinstance(
            values.get("right_arg"), Numeric
        ):
            raise ValueError("One argument must be a register")
        return values

    def create_io_enums(self):
        self._create_input_enum()
        self._create_output_enum()

    def _create_input_enum(self):
        input_name_dict = self._input_register_name_dict(
            [self.left_arg, self.right_arg]
        )
        assert input_name_dict, "At least one argument should be a register"
        self._input_enum = Enum("BinaryOpInputs", input_name_dict)

    def _create_output_enum(self):
        output_name_dict: Dict[str, str] = self._carried_inputs_name_dict()
        output_name_dict[self.output_name] = self.output_name
        if hasattr(self, "garbage_output_name"):
            output_name_dict[self.garbage_output_name] = self.garbage_output_name
        self._output_enum = Enum("BinaryOpOutputs", output_name_dict)

    def _carried_inputs_name_dict(self) -> Dict[str, str]:
        return self._input_register_name_dict(list(self._carried_arguments()))

    def _carried_arguments(self) -> Tuple[Optional[LeftDataT], Optional[RightDataT]]:
        if getattr(self, "inplace", False):
            if isinstance(self.right_arg, RegisterUserInput):
                return self.left_arg, None
            else:
                return None, None
        return self.left_arg, self.right_arg

    @staticmethod
    def _input_register_name_dict(possible_register_args: List[Any]) -> Dict[str, str]:
        name_dict: Dict[str, str] = dict()
        for arg in possible_register_args:
            if isinstance(arg, RegisterUserInput) and arg.name:
                name_dict[arg.name] = arg.name
        return name_dict

    class Config:
        arbitrary_types_allowed = True


class BinaryOpWithIntInputs(
    BinaryOpParams[Union[int, RegisterUserInput], Union[int, RegisterUserInput]]
):
    @pydantic.root_validator()
    def validate_int_registers(cls, values):
        left_arg = values.get("left_arg")
        is_left_arg_float_register = (
            isinstance(left_arg, RegisterUserInput) and left_arg.fraction_places > 0
        )
        right_arg = values.get("right_arg")
        is_right_arg_float_register = (
            isinstance(right_arg, RegisterUserInput) and right_arg.fraction_places > 0
        )
        if is_left_arg_float_register or is_right_arg_float_register:
            raise ValueError("Boolean operation are defined only for integer")

        return values


class BinaryOpWithFloatInputs(
    BinaryOpParams[
        Union[float, FixPointNumber, RegisterUserInput],
        Union[float, FixPointNumber, RegisterUserInput],
    ]
):
    @pydantic.validator("left_arg", "right_arg")
    def convert_numeric_to_fix_point_number(cls, val):
        if isinstance(val, Numeric):
            val = FixPointNumber(float_value=val)
        return val


class BitwiseAnd(BinaryOpWithIntInputs):
    pass


class BitwiseOr(BinaryOpWithIntInputs):
    pass


class BitwiseXor(BinaryOpWithIntInputs):
    pass


class Adder(BinaryOpWithFloatInputs):
    inplace: bool = True


class Subtractor(BinaryOpWithFloatInputs):
    inplace: bool = True


class Multiplier(BinaryOpWithFloatInputs):
    pass


class Comparator(BinaryOpWithFloatInputs):
    output_size: Literal[1] = 1
    _include_equal: bool = pydantic.PrivateAttr(default=True)


class Equal(Comparator):
    pass


class NotEqual(Comparator):
    pass


class GreaterThan(Comparator):
    pass


class GreaterEqual(Comparator):
    pass


class LessThan(Comparator):
    pass


class LessEqual(Comparator):
    pass


class BinaryOpWithLeftRegRightInt(
    BinaryOpParams[RegisterUserInput, pydantic.PositiveInt]
):
    inplace: Literal[True] = True


class LShift(BinaryOpWithLeftRegRightInt):
    pass


class RShift(BinaryOpWithLeftRegRightInt):
    use_arithmetic_bit_shift: bool = True
    garbage_output_name: str = DEFAULT_GARBAGE_OUT_NAME


class CyclicShift(BinaryOpParams[RegisterUserInput, int]):
    inplace: Literal[True] = True
