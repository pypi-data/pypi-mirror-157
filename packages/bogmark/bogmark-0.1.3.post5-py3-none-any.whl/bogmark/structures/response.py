import warnings
from typing import Any

import orjson
from fastapi.responses import ORJSONResponse

from bogmark.logger import get_logger


class JsonResponse(ORJSONResponse):
    total_time = None

    def __init__(
        self, content: Any, status_code: int, media_type: str = None, headers: dict = None, total_time: float = None
    ) -> None:

        super().__init__(content=content, headers=headers, status_code=status_code, media_type=media_type)
        self.status_code = status_code
        self.total_time = total_time
        self.logger = get_logger(__name__, type(self))

    def render(self, content: Any) -> bytes:
        if isinstance(content, bytes):
            return content
        return orjson.dumps(content)

    @property
    def is_ok(self) -> bool:
        return self.status_code < 400

    def as_dict(self):
        warnings.warn('Method "as_dict" is deprecated! Use "to_python_object".', DeprecationWarning, stacklevel=2)
        return self.to_python_object()

    def to_python_object(self):
        if 'application/json' in self.media_type:
            return orjson.loads(self.body)
        self.logger.warning("Use 'body' property to get data.")
