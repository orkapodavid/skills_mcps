"""Runnable bot skeleton with slash commands and argument parsing.

How to use:
- Ensure a valid BDK config.yaml is at ~/.symphony/config.yaml (or edit the loader).
- Install: pip install symphony-bdk-python>=2.0.0
- Run: python bot_slash_command_skeleton.py

This skeleton demonstrates:
1. Simple /hello slash command
2. /help auto-generated command (from descriptions)
3. Parameterized /echo {message} command
4. Proper async structure and datafeed startup
"""

import asyncio
import logging

from symphony.bdk.core.activity.command import CommandContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        activities = bdk.activities()
        messages = bdk.messages()

        @activities.slash("/hello", True, "Say hello to the bot")
        async def hello(ctx: CommandContext):
            """Respond with a greeting including the user's display name."""
            name = ctx.initiator.user.display_name
            await messages.send_message(
                ctx.stream_id,
                f"<messageML>Hello, {name}! 👋</messageML>"
            )

        @activities.slash("/echo {message}", False, "Echo back a message")
        async def echo(ctx: CommandContext):
            """Repeat the user's message back to the stream."""
            text = ctx.arguments.get("message", "(empty)")
            await messages.send_message(
                ctx.stream_id,
                f"<messageML>🔊 {text}</messageML>"
            )

        logger.info("Bot started. Listening for commands...")
        await bdk.datafeed().start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped.")
