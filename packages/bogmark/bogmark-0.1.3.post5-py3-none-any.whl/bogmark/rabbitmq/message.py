from uuid import UUID

import orjson
from aio_pika import IncomingMessage

from bogmark.logger import get_logger
from bogmark.structures.context import get_current_request_id

MAX_RETRIES = 5


class Message:
    __slots__ = ("logger", "payload", "properties", "is_failed", "is_dropped", "is_delayed")

    def __init__(
        self,
        payload: dict,
        properties: dict = None,
        max_retries: int = MAX_RETRIES,
    ):
        self.logger = get_logger(__name__, type(self))
        self.payload = payload

        self.properties = properties or {}
        self.properties.update(
            {
                "current_retries": 0,
                "max_retries": max_retries,
                "request_id": get_current_request_id(),
            }
        )

        self.is_dropped = False
        self.is_delayed = False

    def delay(self):
        if not any([self.is_dropped, self.is_dropped, self.is_delayed]):
            self.is_delayed = True

    def drop(self):
        if not any([self.is_dropped, self.is_dropped, self.is_delayed]):
            self.is_dropped = True

    @property
    def is_processed(self) -> bool:
        return bool(any([self.is_dropped, self.is_delayed]))

    @staticmethod
    def convertors(obj):
        if isinstance(obj, UUID):
            return str(obj)
        raise TypeError

    @property
    def body(self) -> bytes:
        """Dumps message payload and properties into bytes"""
        body_dict = {"payload": self.payload, "properties": self.properties}
        return orjson.dumps(body_dict, default=self.convertors)

    @classmethod
    def from_incoming_message(cls, incoming_message: IncomingMessage):
        body = orjson.loads(incoming_message.body)
        return cls(payload=body["payload"], properties=body["properties"])
