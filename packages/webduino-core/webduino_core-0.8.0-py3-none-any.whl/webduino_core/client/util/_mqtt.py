import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, AsyncIterator, Callable, Tuple

import paho.mqtt.client as mqtt
from asyncio_mqtt import Client, MqttError

MQTT_LOGGER = logging.getLogger("mqtt")


class MQTTClient(Client):
    @asynccontextmanager
    async def filtered_messages(
        self, topic_filter: str, *, queue_maxsize: int = 0, timeout: float = 3
    ) -> AsyncIterator[AsyncGenerator[mqtt.MQTTMessage, None]]:
        """Return async generator of messages that match the given filter.

        Use queue_maxsize to restrict the queue size. If the queue is full,
        incoming messages will be discarded (and a warning is logged).
        If queue_maxsize is less than or equal to zero, the queue size is infinite.

        Example use:
            async with client.filtered_messages('floors/+/humidity') as messages:
                async for message in messages:
                    print(f'Humidity reading: {message.payload.decode()}')
        """
        cb, generator = self._cb_and_generator(
            log_context=f'topic_filter="{topic_filter}"',
            queue_maxsize=queue_maxsize,
            timeout=timeout,
        )
        try:
            self._client.message_callback_add(topic_filter, cb)
            # Back to the caller (run whatever is inside the with statement)
            yield generator
        finally:
            # We are exiting the with statement. Remove the topic filter.
            self._client.message_callback_remove(topic_filter)

    @asynccontextmanager
    async def unfiltered_messages(
        self, *, queue_maxsize: int = 0, timeout: float = 3
    ) -> AsyncIterator[AsyncGenerator[mqtt.MQTTMessage, None]]:
        """Return async generator of all messages that are not caught in filters."""
        # Early out
        if self._client.on_message is not None:
            # TODO: This restriction can easily be removed.
            raise RuntimeError(
                "Only a single unfiltered_messages generator can be used at a time."
            )
        cb, generator = self._cb_and_generator(
            log_context="unfiltered", queue_maxsize=queue_maxsize, timeout=timeout
        )
        try:
            self._client.on_message = cb
            # Back to the caller (run whatever is inside the with statement)
            yield generator
        finally:
            # We are exiting the with statement. Unset the callback.
            self._client.on_message = None

    def _cb_and_generator(
        self, *, log_context: str, queue_maxsize: int = 0, timeout: float
    ) -> Tuple[
        Callable[[mqtt.Client, Any, mqtt.MQTTMessage], None],
        AsyncGenerator[mqtt.MQTTMessage, None],
    ]:
        """
        For adding message received timeout option, overwriting asyncio_mqtt.Client._cb_and_generator function.
        """

        # Queue to hold the incoming messages
        messages: "asyncio.Queue[mqtt.MQTTMessage]" = asyncio.Queue(
            maxsize=queue_maxsize
        )
        # Callback for the underlying API
        def _put_in_queue(
            client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
        ) -> None:
            try:
                messages.put_nowait(msg)
            except asyncio.QueueFull:
                MQTT_LOGGER.warning(
                    f"[{log_context}] Message queue is full. Discarding message."
                )

        # The generator that we give to the caller
        async def _message_generator(timeout) -> AsyncGenerator[mqtt.MQTTMessage, None]:
            # Forward all messages from the queue
            while True:
                # Wait until we either:
                #  1. Receive a message
                #  2. Disconnect from the broker
                get: "asyncio.Task[mqtt.MQTTMessage]" = self._loop.create_task(
                    messages.get()
                )

                try:
                    done, _ = await asyncio.wait(
                        (get, self._disconnected),
                        return_when=asyncio.FIRST_COMPLETED,
                        timeout=timeout,
                    )
                except asyncio.CancelledError:
                    # If the asyncio.wait is cancelled, we must make sure
                    # to also cancel the underlying tasks.
                    get.cancel()
                    raise

                if len(done) == 0:
                    yield None

                if get in done:
                    # We received a message. Return the result.
                    yield get.result()
                else:
                    # We got disconnected from the broker. Cancel the "get" task.
                    get.cancel()
                    # Stop the generator with the following exception
                    raise MqttError("Disconnected during message iteration")

        return _put_in_queue, _message_generator(timeout=timeout)
