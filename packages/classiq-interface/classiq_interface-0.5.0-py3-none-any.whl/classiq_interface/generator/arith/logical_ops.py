from enum import Enum
from typing import Dict, List, Union

import pydantic

from classiq_interface.generator.arith.arithmetic import (
    DEFAULT_ARG_NAME,
    DEFAULT_OUT_NAME,
)
from classiq_interface.generator.arith.fix_point_number import FixPointNumber
from classiq_interface.generator.arith.register_user_input import RegisterUserInput
from classiq_interface.generator.function_params import FunctionParams


class LogicalOps(FunctionParams):
    args: List[Union[RegisterUserInput, FixPointNumber, int, float]]
    output_name: str = DEFAULT_OUT_NAME

    @pydantic.validator("args")
    def validate_inputs_sizes(cls, args):
        for arg in args:
            if isinstance(arg, RegisterUserInput) and (
                arg.size != 1 or arg.fraction_places != 0
            ):
                raise ValueError(
                    f"All inputs to logical and must be of size 1 | {arg.name}"
                )

        return args

    @pydantic.validator("args")
    def set_inputs_names(cls, args):
        for i, arg in enumerate(args):
            if isinstance(arg, RegisterUserInput):
                arg.name = arg.name if arg.name else DEFAULT_ARG_NAME + str(i)

        return args

    def create_io_enums(self):
        input_names: Dict[str, str] = {
            arg.name: arg.name
            for arg in self.args
            if isinstance(arg, RegisterUserInput)
        }
        output_names: Dict[str, str] = {self.output_name: self.output_name}
        output_names.update(input_names)  # out of place funcs
        self._input_enum = Enum("LogicalAndInputs", input_names)
        self._output_enum = Enum("BinaryOpOutputs", output_names)

    class Config:
        arbitrary_types_allowed = True


class LogicalAnd(LogicalOps):
    pass


class LogicalOr(LogicalOps):
    pass
