"""Declarse :class:`JWTPrincipal`."""
from unimatrix.ext.kms import JSONWebToken

from cbra.ext.ioc import Dependency
from .iprincipal import IPrincipal


class JWTPrincipal(Dependency, IPrincipal):
    """A :class:`IPrincipal` implementation using a JSON Web Token (JWT)."""

    def __init__(self):
        super().__init__(use_cache=True)

    async def verify_signature(self, token: JSONWebToken):
        """Verifies the :class:`unimatrix.ext.kms.JSONWebToken` `token`. Raises
        an exception if the signature is not valid.
        """
        raise NotImplementedError
