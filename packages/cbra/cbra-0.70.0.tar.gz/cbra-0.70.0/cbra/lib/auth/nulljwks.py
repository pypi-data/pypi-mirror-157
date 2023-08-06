"""Declares :class:`NullJWKS`."""
from unimatrix.ext.kms import JSONWebKeySet

from cbra.ext.ioc import Dependency


class NullJWKS(Dependency):
    """Resolves to a :class:`~unimatrix.ext.kms.JSONWebKeySet` instance that
    does not contain any keys.
    """

    def __init__(self, is_valid: bool = False):
        self.is_valid = is_valid
        super().__init__()

    class jwks_class(JSONWebKeySet):

        def __init__(self, is_valid: bool = False):
            super().__init__()
            self._is_valid = is_valid

        async def verify(self, *args, **kwargs) -> bool:
            return self._is_valid

    async def resolve(self) -> JSONWebKeySet:
        return self.jwks_class(is_valid=self.is_valid)
