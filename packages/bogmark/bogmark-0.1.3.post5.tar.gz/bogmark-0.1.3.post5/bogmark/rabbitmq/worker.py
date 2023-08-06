import os
import re
import uuid
from abc import abstractmethod

from aio_pika import IncomingMessage, Queue

from bogmark.logger import get_logger

from .connection import AsyncRabbitmq
from .message import Message

# in ms
DEAD_MESSAGE_TTL = 86400000 * 7
RETRY_TIME = 10 * 1000


class Worker:
    DATA_SCHEMA = None

    def __init__(self, async_connection_class: AsyncRabbitmq) -> None:
        if self.DATA_SCHEMA is None:
            raise AttributeError("DATA_SCHEMA should be overwritten")

        self.logger = get_logger(__name__, type(self))

        self._connection: AsyncRabbitmq = async_connection_class
        self._channel = None

    @staticmethod
    def _camel_to_snake(s):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()

    async def _declare_queues_and_exchanges(self, batch_size, fanout_exchange_name):
        # main queue declaration
        await self._channel.set_qos(prefetch_count=batch_size)

        main_exchange = await self._channel.declare_exchange("amq.direct", durable=True)
        queue = await self._channel.declare_queue(
            name=self.queue(),
            durable=True,
            arguments={"x-dead-letter-exchange": "dlx", "x-dead-letter-routing-key": self.dq_queue},
        )
        await queue.bind(main_exchange, routing_key=self.queue())

        # dq queue. Here drop messages with retries
        dlx_exchange = await self._channel.declare_exchange("dlx", durable=True)
        await self._channel.declare_queue(
            name=self.dq_queue,
            durable=True,
            arguments={
                "x-message-ttl": RETRY_TIME,
                "x-dead-letter-exchange": "amq.direct",
                "x-dead-letter-routing-key": self.queue(),
            },
        )
        await queue.bind(dlx_exchange, routing_key=self.dq_queue)

        # xq queue. Here drop totally failed messages
        await self._channel.declare_queue(
            name=self.xq_queue, durable=True, arguments={"x-message-ttl": DEAD_MESSAGE_TTL}
        )

        if fanout_exchange_name:
            fanout_exchange = await self._channel.declare_exchange(
                fanout_exchange_name,
                durable=True,
                type="fanout",
            )
            queue = await self._channel.declare_queue(
                name=self.queue(),
                durable=True,
                arguments={"x-dead-letter-exchange": "dlx", "x-dead-letter-routing-key": self.dq_queue},
            )
            await queue.bind(fanout_exchange, routing_key="")

        return queue

    @classmethod
    def queue(cls):
        queue_prefix = os.environ["QUEUE_PREFIX"].upper()
        queue_name = cls._camel_to_snake(cls.__name__)
        return f"{queue_prefix}_{queue_name}"

    @property
    def xq_queue(self):
        """Que for storing dead messages for DEAD_MESSAGE_TTL"""
        return f"{self.queue()}.XQ"

    @property
    def dq_queue(self):
        """Que for requeue messages after RETRY_TIME"""
        return f"{self.queue()}.DQ"

    async def processing(self, queue, batch_size):
        batch_id = str(uuid.uuid4())
        current_messages = []

        async with queue.iterator() as queue_iter:
            async for incoming_message in queue_iter:

                self.logger.info(
                    "Start processing batch[{}] 0/{}".format(batch_id, batch_size),
                    extra={"worker": type(self).__name__, "queue": self.queue(), "batch_size": batch_size},
                )

                incoming_message: IncomingMessage
                self.logger.info(
                    ("Start processing message %s" % incoming_message.message_id),
                    extra={"worker": type(self).__name__, "queue": self.queue(), "batch_size": batch_size},
                )
                try:
                    current_message: Message = Message.from_incoming_message(
                        incoming_message=incoming_message,
                    )

                    current_messages.append(current_message)
                    len_current_messages = len(current_messages)
                    if len_current_messages % batch_size != 0:
                        self.logger.info(
                            "Current batch[{}] size is {}/{}. Waiting".format(
                                batch_id, len_current_messages, batch_size
                            )
                        )
                        continue
                    if batch_size == 1:
                        await self.on_message(current_message)
                    else:
                        await self.on_batch_messages(current_messages)
                except Exception as e:
                    self.logger.exception(
                        e,
                        extra={
                            "worker": self.__class__.__name__,
                            "queue": self.queue(),
                        },
                    )
                    for cur_msg in current_messages:
                        await self._connection.publish(
                            message=cur_msg,
                            routing_key=self.xq_queue,
                        )

                self.logger.info(
                    "End processing batch[{}]".format(batch_id),
                    extra={"worker": type(self).__name__, "queue": self.queue()},
                )
                current_messages = []
                batch_id = str(uuid.uuid4())

                await incoming_message.ack(multiple=True)

    @abstractmethod
    async def on_message(self, message: Message):  # noqa: U100
        """Perform worker logic"""
        raise NotImplementedError

    @abstractmethod
    async def on_batch_messages(self, messages: list[Message]):  # noqa: U100
        """Perform batch worker logic"""
        raise NotImplementedError

    async def consume(self, batch_size: int = 1, fanout_exchange_name: str = None):
        """Start consuming.
        If lost rabbit connection: put message in xq and stop consuming
        If exception occurred: put message in xq and continue consuming
        """

        if batch_size <= 0:
            raise ValueError("batch_size should be > 0")

        channel = await self._connection.get_channel()
        self._channel = channel

        queue: Queue = await self._declare_queues_and_exchanges(
            fanout_exchange_name=fanout_exchange_name, batch_size=batch_size
        )
        self.logger.info(
            "Start consuming",
            extra={
                "worker": type(self).__name__,
                "queue": self.queue(),
                "batch_size": batch_size,
            },
        )

        await self.processing(queue, batch_size)
