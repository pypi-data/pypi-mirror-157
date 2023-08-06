import enum
import sys

import aio_pika
from aio_pika import DeliveryMode
from aio_pika import Message as AioPikaMessage
from aiormq.types import DeliveredMessage

from bogmark.logger import get_logger

from .message import Message

logger = get_logger(__name__)


class ConnectionType(enum.Enum):
    PUBLISHER = "publisher"
    CONSUMER = "consumer"


class NoRequestIdExceptionError(Exception):
    pass


class NoQueueExistsError(Exception):
    pass


class CustomRobustConnection(aio_pika.RobustConnection):
    def _on_connection_close(self, connection, closing, *args, **kwargs):  # noqa: U100
        if self.reconnecting:
            return

        self.connected.clear()
        self.connection = None

        super()._on_connection_close(connection, closing)

        if self._closed:
            return

        logger.error("Connection to %s closed", self)
        sys.exit()


class AsyncRabbitmq:
    async_connections = {}

    def __init__(self, host: str, port: int, login: str, password: str, virtual_host: str, ssl: bool):
        self.logger = get_logger(__name__, type(self))
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.ssl = ssl
        self.virtual_host = virtual_host

    async def get_connection(self, connection_type: ConnectionType):
        self.logger.info("Getting rmq connection")
        conn = self.async_connections.get(connection_type)
        if conn is None:
            conn = await aio_pika.connect(
                host=self.host,
                port=self.port,
                login=self.login,
                password=self.password,
                virtualhost=self.virtual_host,
                timeout=10,
                ssl=self.ssl,
                connection_class=CustomRobustConnection,
            )
            self.async_connections[connection_type] = conn
        return conn

    async def get_channel(self):
        self.logger.info("Getting channel")
        conn = await self.get_connection(ConnectionType.PUBLISHER)
        channel = await conn.channel()
        return channel

    async def publish(self, message: Message, routing_key: str = "", exchange_name: str = ""):
        """Publish message in queue but within async framework (thread save)

        :param message: payload
        :param exchange_name:
        :param str routing_key: routing key to publish in
        """
        conn = await self.get_connection(ConnectionType.PUBLISHER)
        async with conn.channel() as channel:
            if exchange_name:
                exch = await channel.get_exchange(exchange_name)
            else:
                exch = channel.default_exchange

            self.logger.info('Publishing message. Exchange: {}. Routing key: {}" '.format(exchange_name, routing_key))
            r = await exch.publish(
                routing_key=routing_key,
                message=AioPikaMessage(
                    body=message.body,
                    delivery_mode=DeliveryMode.PERSISTENT,
                    content_type="application/json",
                ),
            )
            if isinstance(r, DeliveredMessage):
                # should be Basic.Ack from pamqp.specifications
                self.logger.error(f"No route to {r.delivery.routing_key}. Sheeesh, did someone delete the queue?")
                raise NoQueueExistsError(
                    "No queue for routing_key `%s` in exchange `%s`" % (routing_key, exchange_name)
                )
            return True
