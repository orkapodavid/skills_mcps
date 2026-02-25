"""RealTimeEventListener bot — subscribes to datafeed events.

Demonstrates:
1. Subclassing RealTimeEventListener to react to messages and room events
2. Subscribing a listener to the datafeed loop
3. Proper async startup and shutdown

Usage:
    pip install symphony-bdk-python>=2.0.0
    python realtime_listener_bot.py
"""

import asyncio
import logging

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.core.service.datafeed.real_time_event_listener import (
    RealTimeEventListener,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EchoListener(RealTimeEventListener):
    """Echoes incoming messages and logs room join events."""

    def __init__(self, message_service):
        self._messages = message_service

    async def on_message_sent(self, initiator, event):
        """Reply to every message with a greeting."""
        stream_id = event.message.stream.stream_id
        user_name = initiator.user.display_name
        logger.info("Message from %s in stream %s", user_name, stream_id)
        await self._messages.send_message(
            stream_id,
            f"<messageML>Hello, {user_name}! I received your message.</messageML>",
        )

    async def on_user_joined_room(self, initiator, event):
        """Welcome a user who joins a room."""
        stream_id = event.stream.stream_id
        user_name = event.affected_user.display_name
        logger.info("User %s joined room %s", user_name, stream_id)
        await self._messages.send_message(
            stream_id,
            f"<messageML>Welcome to the room, {user_name}! 🎉</messageML>",
        )


async def main():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        listener = EchoListener(bdk.messages())
        bdk.datafeed().subscribe(listener)
        logger.info("Datafeed listener started. Waiting for events...")
        await bdk.datafeed().start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Listener stopped.")
