# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import fastapi.routing
from fastapi.dependencies.utils import get_body_field
from fastapi.dependencies.utils import get_dependant


class APIRoute(fastapi.routing.APIRoute):
    """A custom :class:`fastapi.routing.APIRoute` implementation
    that accomodates the rendering of request examples for multiple
    content types.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        # Inspect the APIRoute.endpoint attribute to determine if we
        # need to do some magic the get a proper body model. Since
        # a number of handler functions does not declare the body
        # model using annotation, in order to be able to do explicit
        # parsing of the request body, it is not seen by FastAPI when
        # creating a route and rendering the OpenAPI schema. Thus, here
        # we look for some special types from which we can retrieve the
        # body model. This ensures that all models used by Endpoint
        # implementations are added to the schema.
        Model = getattr(self.endpoint, 'model', None)
        if Model is not None:
            # Create a fake dependant to trick get_body_field() into
            # getting the model.
            async def f(dto: Model): pass
            self.body_field = get_body_field(
                dependant=get_dependant(path=self.path_format, call=f),
                name=self.unique_id
            )
