import traceback
from functools import partial

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.responses import ORJSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class BizLogicError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


def http_exception(request, exc: HTTPException, include_traceback):  # noqa
    response_data = {
        "error": {
            "message": exc.detail,
        }
    }
    status_code = getattr(exc, "status_code", 500)
    if status_code == 422:
        return ORJSONResponse(content=exc.detail, status_code=status_code)

    # Invalid API headers
    if status_code == 415:
        response_data = {
            "error": {
                "message": exc.detail,
            }
        }
        return ORJSONResponse(content=response_data, status_code=status_code, headers=exc.headers)

    if include_traceback:
        response_data["error"]["traceback"] = "".join(traceback.format_tb(exc.__traceback__))

    return ORJSONResponse(content=response_data, status_code=status_code)


def application_exception(request, exc, include_traceback):  # noqa
    response_data = {
        "error": {
            "message": "Server Error",
        }
    }
    if include_traceback:
        response_data["error"]["traceback"] = "".join(traceback.format_tb(exc.__traceback__))
    status_code = getattr(exc, "status_code", 500)
    return ORJSONResponse(content=response_data, status_code=status_code)


def register_errors(app, include_traceback=False):
    app.add_exception_handler(
        StarletteHTTPException,
        partial(http_exception, include_traceback=include_traceback),
    )
    app.add_exception_handler(
        Exception,
        partial(application_exception, include_traceback=include_traceback),
    )
