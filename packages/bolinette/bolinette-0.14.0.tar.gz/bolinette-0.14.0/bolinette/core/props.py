from abc import ABC
import itertools
from collections.abc import Iterator
from typing import TypeVar

from bolinette import core

_T = TypeVar("_T")


class Properties(ABC):
    def __init__(self, parent):
        self.parent = parent

    @staticmethod
    def _get_cls_attributes_of_type(
        obj: type, attr_type: type[_T]
    ) -> Iterator[tuple[str, _T]]:
        parent_attrs = (
            Properties._get_cls_attributes_of_type(parent, attr_type)
            for parent in obj.__bases__
        )
        return itertools.chain(
            *parent_attrs,
            (
                (name, attribute)
                for name, attribute in vars(obj).items()
                if isinstance(attribute, attr_type)
            )
        )

    @staticmethod
    def _get_attributes_of_type(obj, attr_type):
        return (
            (name, attribute)
            for name, attribute in vars(obj).items()
            if isinstance(attribute, attr_type)
        )

    def get_instantiable(
        self, of_type: type[core.abc.T_Instance]
    ) -> Iterator[tuple[str, "core.InstantiableAttribute[core.abc.T_Instance]"]]:
        attrs = self._get_cls_attributes_of_type(
            type(self.parent), core.InstantiableAttribute
        )
        return ((name, attr) for name, attr in attrs if attr.type == of_type)
