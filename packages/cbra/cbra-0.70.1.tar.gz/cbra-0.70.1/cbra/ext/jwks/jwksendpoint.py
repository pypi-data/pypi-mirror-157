"""Declares :class:`JWKSEndpoint`."""
import typing

import fastapi
from ckms.types import JSONWebKeySet

import cbra


class JWKSEndpoint(cbra.Endpoint):
    """Single-tenant endpoint exposing the public keys used by the server to
    verify signatures and encrypt data, as a JSON Web Key Set (JWKS).
    """
    __module__: str = 'cbra.ext.jwks'
    name: str = 'metadata.jwks'
    description: str = (
        "Provides the JSON Web Key Set (JWKS) that a client may use to "
        "encrypt data (sent to the server) or verify signatures (issued "
        "by the server)."
    )
    method: str = 'GET'
    mount_path: str = '.well-known/jwks.json'
    summary: str = 'JSON Web Key Set (JWKS)'
    response_model: type[JSONWebKeySet] = JSONWebKeySet
    response_description: str = "The server public keys."
    tags: list[str] = ["Server metadata"]

    @staticmethod
    def get_server_jwks(request: cbra.Request) -> JSONWebKeySet:
        return request.app.jwks

    def __init__(self, jwks: JSONWebKeySet = fastapi.Depends(get_server_jwks)):
        self.jwks = jwks

    async def handle(self) -> dict[str, typing.Any]:
        return self.jwks.dict(exclude_defaults=True)