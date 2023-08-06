"""Declares :class:`NullJWTPrincipal`."""
from unimatrix.ext.kms import JSONWebToken

from .jwtprincipal import JWTPrincipal


class NullJWTPrincipal(JWTPrincipal):

    def __init__(self, **claims):
        self.claims = claims
        super().__init__()

    async def resolve(self):
        return JSONWebToken.new(**self.claims)
