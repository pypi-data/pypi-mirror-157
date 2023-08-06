import os
import pathlib
import sys
import time
import traceback
from typing import Any, Union
from uuid import UUID

import dotenv
import httpx
import orjson
from pydantic import AnyHttpUrl, BaseSettings, Field, validator

from bogmark.logger import get_logger
from bogmark.structures.context import get_current_request_id
from bogmark.structures.response import JsonResponse


class BaseConfig(BaseSettings):
    @validator("URL", check_fields=False)
    def strip_slash(cls, field):
        return field.rstrip("/")


class BaseAsyncRequester:
    def __init__(self, base_url=None, login=None, password=None, retries=5):
        self.load_env()
        self.base_url = base_url.rstrip("/") if base_url else self.get_base_url()
        self.service_name = os.environ["SERVICE_NAME"]
        self.logger = get_logger(__name__, type(self))
        self.login = login
        self.password = password

        transport = httpx.AsyncHTTPTransport(retries=retries)
        self.client = httpx.AsyncClient(transport=transport)

    class Config(BaseConfig):
        URL: AnyHttpUrl = Field(default="http://localhost")

    async def close(self) -> Any:
        await self.client.aclose()

    @staticmethod
    def load_env():
        for p in sys.path:
            env_path = pathlib.Path(p, "settings", ".env")
            if env_path.exists():
                dotenv.load_dotenv(env_path.as_posix())
                break

    @classmethod
    def get_base_url(cls, **kwargs):
        return cls.Config().URL

    def _get_headers(self):
        return {
            "X-REQUEST-ID": get_current_request_id(),
            "X-SERVICE-NAME": self.service_name,
        }

    @classmethod
    def convertors(cls, obj):
        if isinstance(obj, UUID):
            return str(obj)
        raise TypeError

    @classmethod
    def custom_orjson_encoder(cls, v):
        return orjson.dumps(v, default=cls.convertors).decode()

    async def _log_request(
        self,
        log_level,
        response: httpx.Response = None,
        total_time: float = None,
        before_request: bool = False,
        raise_for_4xx: bool = True,
        **kwargs,
    ):
        log_functions = {"INFO": self.logger.info, "ERROR": self.logger.error, "WARN": self.logger.warning}
        logger = log_functions[log_level.upper()]
        cls_name = self.__class__.__name__

        if before_request:
            logger(msg=f"Sending request via {cls_name}", extra=kwargs)
            return

        msg = f"Response from {cls_name}({response.url})"
        extra = {"status_code": response.status_code, "url": str(response.url), "total_time": total_time}
        if response.status_code >= 400:
            if raise_for_4xx or 500 <= response.status_code < 600:
                logger = log_functions["ERROR"]
                msg = f"{cls_name}({response.url}) answered {response.status_code}"
        logger(msg=msg, extra=extra)

    async def _make_request(
        self,
        method: str,
        url: str,
        headers: dict = None,
        json: Union[dict, list] = None,
        data: Union[dict, str, bytes] = None,
        files: dict = None,
        params: dict = None,
        timeout: float = 25,
        raise_for_4xx=True,
    ):
        if data and json and files:
            raise ValueError("you can only pass `data` or `json` or `files`")

        headers = headers or {}

        if json:
            headers["content-type"] = "application/json; charset=utf-8"
            data = self.custom_orjson_encoder(json)

        headers.update(self._get_headers())
        auth = (self.login, self.password)
        request_params = {
            "method": method.lower(),
            "url": url,
            "params": params,
            "headers": headers,
            "timeout": timeout,
            "data": data,
            "files": files,
            "auth": auth if all(auth) else None,
        }
        request_params = {k: v for k, v in request_params.items() if v is not None}
        start_time = time.perf_counter()
        try:
            await self._log_request(before_request=True, log_level="INFO", url=request_params["url"])
            response: httpx.Response = await self.client.request(**request_params)
            total_time = time.perf_counter() - start_time
            content_type = response.headers["content-type"]
            response_content = await response.aread()

            await self._log_request(
                before_request=False,
                log_level="INFO",
                response=response,
                total_time=total_time,
                method=method.upper(),
                raise_for_4xx=raise_for_4xx,
            )
            return JsonResponse(
                total_time=total_time,
                status_code=response.status_code,
                content=response_content,
                media_type=content_type,
                headers=response.headers,
            )

        except Exception as e:
            self.logger.error(e, exc_info=True, extra={"stack": "".join(traceback.format_stack())})
            total_time = time.perf_counter() - start_time
            content = {"error": {"message": f"{e}"}}
            return JsonResponse(
                total_time=total_time,
                status_code=500,
                content=content,
            )
