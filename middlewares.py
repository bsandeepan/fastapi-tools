import logging
from uuid import uuid4

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic.error_wrappers import ValidationError
from starlette.types import ASGIApp
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        I felt lazy to add error handling try-excepts everywhere for any weird error.
        Hence a centralized error handling middleware! :)

        It also adds a unique request identifier for easy debugging.
        - Sandeepan B.

        This is a boilerplate code that can be reused in other apps.

        :param request:     An contextual object that inherits from Starlette Request.
        :param call_next:   This is a reference function that passes the request to the
                            intended endpoint. If you know Express-NodeJS, then this is
                            similar to next function in express middlewares. We use this
                            function either after processing is done here, or in middle
                            if we need to modify the generated response.

        :return:            Response received from call_next(), or an error response.
        """

        try:
            request.state.request_id = uuid4().__str__()
            return await call_next(request)

        except HTTPException as e:
            self.logger.exception(repr(e), extra={"request_id": request.state.request_id})
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        except ValidationError as e:
            # Some pydantic model validation failed because of invalid input
            self.logger.exception(repr(e), extra={"request_id": request.state.request_id})
            # error_dict = {err['loc'][0]: err['msg'] for err in e.errors()}
            return JSONResponse(status_code=400, content={"detail": "Invalid request params"})

        except Exception as e:
            self.logger.exception(repr(e), extra={"request_id": request.state.request_id})
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

        except BaseException as e:
            self.logger.exception(repr(e), extra={"request_id": request.state.request_id})
            return JSONResponse(status_code=500, content={"detail": "Call a Developer. NOW!!!"})


class RequestIdentifierMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
            Middleware to add unique request identifier for easy debugging. Error Handling
            needs to be implemented in app carefully.

            :param request:     An contextual object that inherits from Starlette Request.
            :param call_next:   After modifying request, pass it to the app endpoint.

            :return:            Response received from call_next().
            """
        request.state.request_id = uuid4().__str__()
        return await call_next(request)
