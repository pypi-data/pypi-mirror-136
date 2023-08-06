import abc
from enum import Enum
from typing import Any, List, Optional, Type

import pydantic
from pydantic.fields import ModelPrivateAttr

DEFAULT_OUTPUT_NAME = "OUT"
DEFAULT_INPUT_NAME = "IN"


class DefaultInputEnum(Enum):
    pass


class DefaultOutputEnum(Enum):
    OUT = DEFAULT_OUTPUT_NAME


class IO(Enum):
    Input = "Input"
    Output = "Output"


def input_io(is_inverse: bool) -> IO:
    if is_inverse:
        return IO.Output
    return IO.Input


def output_io(is_inverse: bool) -> IO:
    if is_inverse:
        return IO.Input
    return IO.Output


class FunctionParams(pydantic.BaseModel, abc.ABC):
    _input_enum: Type[Enum] = pydantic.PrivateAttr(default=None)
    _output_enum: Type[Enum] = pydantic.PrivateAttr(default=None)

    _input_names: List[str] = pydantic.PrivateAttr(default_factory=list)
    _output_names: List[str] = pydantic.PrivateAttr(default=[DEFAULT_OUTPUT_NAME])

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.create_io_enums()
        self._create_io_names()

    def get_io_enum(self, io: IO) -> Type[Enum]:
        if io == IO.Input:
            return self._input_enum
        elif io == IO.Output:
            return self._output_enum
        raise AssertionError("Unsupported IO type")

    def get_io_names(self, io: IO, is_inverse: bool = False) -> List[str]:
        assert io == IO.Input or io == IO.Output, "Unsupported IO type"
        if (io == IO.Input) ^ is_inverse:
            return self._input_names
        else:
            return self._output_names

    def create_io_enums(self) -> None:
        pass

    def _create_io_names(self) -> None:
        if self._input_enum is None and self._output_enum is None:
            return

        self._input_names = list(self._input_enum.__members__.keys())
        self._output_names = list(self._output_enum.__members__.keys())

    def is_valid_io_name(self, name: str, io: IO) -> bool:
        return name in self.get_io_names(io)

    @classmethod
    def get_default_input_names(cls) -> Optional[List[str]]:
        return cls._get_io_name_default_if_exists(io_attr_name="_input_names")

    @classmethod
    def get_default_output_names(cls) -> Optional[List[str]]:
        return cls._get_io_name_default_if_exists(io_attr_name="_output_names")

    @classmethod
    def _is_default_create_io_method(cls) -> bool:
        return (
            cls._create_io_names == FunctionParams._create_io_names
            and cls.create_io_enums == FunctionParams.create_io_enums
        )

    @classmethod
    def _get_io_name_default_if_exists(cls, io_attr_name: str) -> Optional[List[str]]:
        if not cls._is_default_create_io_method():
            return None

        attr: ModelPrivateAttr = cls.__private_attributes__[io_attr_name]
        return attr.get_default()
