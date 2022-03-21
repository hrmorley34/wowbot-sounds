from typing import Any, Dict, Generic, Iterator, Mapping, TypeVar
from pydantic import BaseModel as _BaseModel, Extra, validator
from pydantic.generics import GenericModel


class BaseModel(_BaseModel, extra=Extra.forbid):
    pass


class DescriptionOptionalMixin(BaseModel):
    description: str = ""


NameT = TypeVar("NameT", bound=str)


class NamedMixin(GenericModel, Generic[NameT], BaseModel):
    name: NameT


VT = TypeVar("VT", bound=NamedMixin[Any])


class NameKeyDict(GenericModel, Generic[NameT, VT], Mapping[NameT, VT], BaseModel):
    __root__: Dict[NameT, VT]

    @validator("__root__", pre=True)
    def add_keys(cls, values: Dict[NameT, Dict[str, Any]]):
        new_values: Dict[NameT, Dict[str, Any]] = dict()
        for name in values:
            new_values[name] = values[name].copy()
            new_values[name]["name"] = name
        return new_values

    def __getitem__(self, key: NameT) -> VT:
        return self.__root__.__getitem__(key)

    def __iter__(self) -> Iterator[NameT]:  # type: ignore
        return self.__root__.__iter__()

    def __len__(self) -> int:
        return self.__root__.__len__()
