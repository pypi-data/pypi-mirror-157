import itertools
import logging
from dataclasses import dataclass, field

from fastapi import APIRouter, Depends, FastAPI, Request, Response
from fastapi.responses import ORJSONResponse, PlainTextResponse
from starlette_prometheus import metrics

from bogmark.server.middlewares import headers, logs, prometheus

from .dependecies import check_headers
from .errors import register_errors
from .responses import ErrorSchemaResponse

logger = logging.getLogger(__name__)


@dataclass
class CustomRouter:
    router: APIRouter
    prefix: str = ""
    tags: list[str] = field(default_factory=list)
    dependencies: list[Depends] = field(default_factory=list)
    default_response_class: Response = ORJSONResponse
    disable_check_headers: bool = False
    include_in_schema: bool = True
    deprecated: bool = False


def basic_ping_endpoint():
    return PlainTextResponse("pong")


def healthz_endpoint():
    return {"temperature": 36.6}


def metrics_endpoint(request: Request):
    return metrics(request)


def set_error_response_openapi(description: str = ""):
    return {"description": description, "model": ErrorSchemaResponse}


def register_routers(
    title: str = "Api",
    description: str = "",
    routers: list[list[CustomRouter]] = (),
    on_startup=(),
    on_shutdown=(),
    openapi_url="/openapi.json",
    ping_endpoint=None,
    version: str = "0.1.0",
    enable_logging_middleware: bool = True,
    include_traceback: bool = False,
    **kwargs,
):
    """

    :param include_traceback: include traceback into response
    :param enable_logging_middleware: enable logging middleware
    :param routers: compiled routers from `compile_routers` function
    :param on_startup: a list of coroutines to call before server startup
    :param on_shutdown: a list of coroutines to call before server shutdown
    :param openapi_url: openapi_url
    :param ping_endpoint: a handler for readiness probes
    :param version: api version
    :param kwargs: all fastApi related kwargs
    :return: FastApi app
    """

    if ping_endpoint is None:
        ping_endpoint = basic_ping_endpoint

    app = FastAPI(
        title=title,
        description=description,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        openapi_url=openapi_url,
        version=version,
        **kwargs,
    )
    register_errors(app, include_traceback=include_traceback)
    headers.register(app)
    prometheus.register(app)
    if enable_logging_middleware:
        logs.register(app)

    for custom_router in itertools.chain(*routers):
        app.include_router(
            router=custom_router.router,
            tags=custom_router.tags,
            prefix=custom_router.prefix,
            include_in_schema=custom_router.include_in_schema,
            deprecated=custom_router.deprecated,
            dependencies=custom_router.dependencies,
        )
    app.add_api_route(path="/readiness", endpoint=ping_endpoint, tags=["Probes"], include_in_schema=False)
    app.add_api_route(path="/liveness", endpoint=healthz_endpoint, tags=["Probes"], include_in_schema=False)
    app.add_api_route(path="/metrics", endpoint=metrics_endpoint, tags=["Probes"], include_in_schema=False)
    return app


def compile_routers(routers: list[CustomRouter], root_prefix: str = "", dependencies=None) -> list[CustomRouter]:
    compiled_routers = []
    common_dependencies = dependencies or []
    for router in routers:
        router: CustomRouter

        dependencies = router.dependencies
        dependencies.extend(common_dependencies)
        router.dependencies.extend(dependencies)

        if not router.disable_check_headers:
            dependencies.append(check_headers)

        router.prefix = root_prefix + router.prefix
        router.dependencies = [Depends(d) for d in dependencies]
        compiled_routers.append(router)

    return compiled_routers
