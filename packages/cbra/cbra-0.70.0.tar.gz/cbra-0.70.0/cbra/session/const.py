"""Declares constants used by the :mod:`cbra.session` module."""
from cbra.conf import settings # type: ignore


SESSION_COOKIE_NAME: str = (
    getattr(settings, 'SESSION_COOKIE_NAME', None) # type: ignore
    or 'session-claims'
)

SESSION_SIGNING_KEY: str = (
    getattr(settings, 'SESSION_SIGNING_KEY', None) # type: ignore
    or 'session-signing-key'
)

SESSION_ENCRYPTION_KEY: str = (
    getattr(settings, 'SESSION_ENCRYPTION_KEY', None) # type: ignore
    or 'session-encryption-key'
)

SESSION_ENCRYPTION_ALG: str = (
    getattr(settings, 'SESSION_ENCRYPTION_ALG', None) # type: ignore
    or 'A256GCM'
)