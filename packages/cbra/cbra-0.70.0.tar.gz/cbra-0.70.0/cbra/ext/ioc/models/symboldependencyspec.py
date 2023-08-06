"""Declares :class:`SymbolDependencySpec`."""
import typing

from ..loader import import_symbol
from .dependencyspec import DependencySpec


class SymbolDependencySpec(DependencySpec):
    """Specifies the configuration format for a dependency that is loaded
    from the qualified name of a Python symbol.
    """
    __module__: str = 'cbra.ext.ioc.models'
    type: typing.Literal['symbol'] = 'symbol'
    qualname: str

    async def resolve(self) -> typing.Any:
        """Resolve the dependency specified by the input parameters."""
        return import_symbol(self.qualname)
