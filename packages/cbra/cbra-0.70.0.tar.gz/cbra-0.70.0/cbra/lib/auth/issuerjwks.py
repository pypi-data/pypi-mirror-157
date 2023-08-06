"""Declares :class:`IssuerJWKS`."""
import asyncio
import functools
import logging
import operator

from fastapi.params import Depends
from unimatrix.ext.kms import keychain
from unimatrix.ext.kms import JSONWebKeySet
from unimatrix.ext.kms.loaders import JWKSLoader


class IssuerJWKS(Depends):
    """A :class:`fastapi.params.Depends` implementation that discovers the
    JSON Web Key Set (JWKS) of the given list of issuers through the OpenID
    or OAuth 2.0 discovery metadata.
    """
    __module__: str = 'cbra.lib.auth'
    logger: logging.Logger = logging.getLogger('uvicorn')

    def __init__(self, issuers: list):
        self.issuers = issuers
        self.loader = JWKSLoader()
        super().__init__(self.resolve, use_cache=True)

    async def resolve(self) -> JSONWebKeySet:
        jwks = JSONWebKeySet()
        futures = []
        for issuer in self.issuers:
            futures.append(self._load(keychain, self.loader, issuer))
        keysets = [x for x in await asyncio.gather(*futures) if x is not None]
        return functools.reduce(operator.add, [jwks] + keysets)

    async def _load(self, keychain, loader, issuer):
        jwks = await keychain.get_issuer_jwks(issuer)
        if jwks is None:
            jwks = await loader.discover(issuer)
            if jwks is not None:
                await keychain.persist(jwks, issuer=issuer)
                self.logger.info("Imported keys (issuer: %s)", issuer)
        return jwks
