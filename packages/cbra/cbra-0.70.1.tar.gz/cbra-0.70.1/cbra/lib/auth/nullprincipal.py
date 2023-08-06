"""Declares :class:`NullPrincipal`."""
from cbra.ext.ioc import Dependency

from .iprincipal import IPrincipal


class NullPrincipal(Dependency, IPrincipal):
    """A :class:`IPrincipal` implementation that never authenticates a
    principal and as a result is always ``None``.
    """
    __module__: str = 'cbra.lib.auth'

    def __init__(self, *args, **kwargs):
        super().__init__(use_cache=True)

    async def resolve(self) -> None: # pragma: no cover
        return None
