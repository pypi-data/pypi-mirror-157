"""Declares :class:`BaseRequestHandler`."""
import asyncio
from email.policy import default
import inspect
import logging
import typing

import fastapi
import fastapi.responses

from cbra.ext.ioc.dependency import Dependency
from .. import headers
from ..dependantsignature import DependantSignature
from ..lib import auth
from ..utils import PositionalArgument
from ..utils import order_parameters
from ..exceptions import CanonicalException


class BaseRequestHandler:
    """The base class for all request handler implementations."""
    _ignored_parameters: set = {'request', 'response', 'principal'}
    _is_coroutine = asyncio.coroutines._is_coroutine
    logger: logging.Logger = logging.getLogger('uvicorn')
    __module__: str = 'cbra.handler'

    # These are set during add_to_router()
    path: str

    #: The name of the handler as shown in the API documentation.
    name: str = None

    #: The summary as shown in the API documentation.
    summary: str = None

    #: Description of the request handler.
    description: str = None

    #: Specifies the response model for this handler.
    returns: type = None

    #: A dictionary of annotatios for the handler.
    annotations: dict = None

    # The default status code
    status_code: int = 200

    #: The principal dependency resolver.
    principal: auth.IPrincipal = auth.NullPrincipal()

    #: The principal dependency resolver class.
    principal_class: type = auth.NullPrincipal

    #: The description of the response.
    response_description: str = "Sucess"

    #: Mapping of response code to models
    responses: typing.Dict[int, typing.Any] = {}

    @property
    def __signature__(self) -> inspect.Signature:
        params = [
            PositionalArgument('request', fastapi.Request),
            PositionalArgument('response', fastapi.responses.Response),
            PositionalArgument(
                name='origin',
                annotation=typing.Optional[str],
                default=headers.ORIGIN
            )
        ]
        try:
            params.extend(self.get_signature_parameters())
            params.extend([
                PositionalArgument('principal',
                    default=self.get_principal_dependency())
            ])
        except Exception:
            raise
        return inspect.Signature(
            parameters=order_parameters(params),
            return_annotation=self.returns or inspect.Signature.empty
        )

    def __init__(self,
        method: str,
        returns: type = None,
        principal: auth.IPrincipal = None,
        principal_class: type = None,
        summary: typing.Optional[str] = None,
        response_description: typing.Optional[str] = None
    ):
        self.method = method
        self.returns = returns or self.returns
        self.principal = principal or self.principal
        self.principal_class = principal_class or self.principal_class
        if response_description is not None:
            self.response_description = response_description
        self.summary = summary or self.summary
        self.signature = DependantSignature(self)

    def add_to_router(
        self,
        app: typing.Union[fastapi.FastAPI, fastapi.APIRouter],
        path: str,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Add a request handler to a router."""
        kwargs.setdefault('name', self.name)
        kwargs.setdefault('summary', self.summary)
        kwargs.setdefault('description',
            self.description or self.handle.__doc__)
        kwargs.setdefault('response_description', self.response_description)
        dependencies = kwargs.setdefault('dependencies', [])
        dependencies.extend(self.get_dependencies())

        # Add some default responses.
        app.add_api_route(
            path=path,
            endpoint=self,
            status_code=self.status_code,
            methods=[self.method],
            *args,
            **{**kwargs, **self.get_router_kwargs()}
        )

        # Update internal state
        self.path = path

    def get_dependencies(self) -> list: # pragma: no cover
        """Return the list of dependencies that are not injected into the
        function call.
        """
        return self.signature.get_request_dependencies()

    def get_handler_args(self, *args, **kwargs) -> tuple:
        """Return the positional arguments that are passed to the request
        handler function.
        """
        return []

    def get_handler_kwargs(self, *args, **kwargs) -> tuple:
        """Return the keyword arguments that are passed to the request
        handler function.
        """
        return kwargs

    def get_router_kwargs(self) -> dict:
        """Return a dictionary containing the keyword arguments passed when
        registering the route.
        """
        return {}

    def get_principal_dependency(self) -> Dependency:
        """Return the :class:`cbra.Dependency` used to inject the current
        principal.
        """
        return self.principal

    def get_signature_parameters(self) -> typing.List[inspect.Parameter]: # pragma: no cover
        """Get the list of :class:`inspect.Parameter` instances specifying
        the callables' signature.
        """
        return []

    def get_type_annotations(self) -> dict: # pragma: no cover
        """Return the dictionary containing the type annotations."""
        return {}

    async def handle(self, *args, **kwargs):
        """Handles the request. The default implementation always raises
        :exc:`NotImplementedError`.
        """
        raise NotImplementedError

    async def run_handle(self, *args, **kwargs):
        """Invokes :meth:`run_handle()`."""
        return await self.handle(*args, **kwargs)

    async def __call__(self,
        request: fastapi.Request,
        response: fastapi.responses.Response,
        *args,
        **kwargs
    ) -> typing.Any:
        """Resolve dependencies and invoke :meth:`handle()`."""
        try:
            result = await self.run_handle(
                request=request,
                response=response,
                *self.get_handler_args(*args, **kwargs),
                **self.get_handler_kwargs(*args, **kwargs)
            )
        except CanonicalException as exc:
            result = exc
        return await self.process_result(
            request=request,
            response=response,
            result=result,
            exception=isinstance(result, CanonicalException)
        )

    async def process_result(self,
        request: fastapi.Request,
        response: fastapi.responses.Response,
        result: typing.Union[typing.Any, CanonicalException],
        exception: bool = None
    ) -> typing.Any:
        """Process the result of the handler invocation prior to returing
        a response to the client.
        """
        if exception:
            response.status_code = result.http_status_code
            response.headers.update(result.http_headers)
            return result.as_dict()

        return result
