"""Form Activity bot — handles Symphony Elements form submissions.

Demonstrates:
1. Sending an Elements form via MessageML
2. Handling form submissions with FormReplyActivity
3. Extracting form values from FormReplyContext

Usage:
    pip install symphony-bdk-python>=2.0.0
    python form_activity_bot.py
"""

import asyncio
import logging

from symphony.bdk.core.activity.command import CommandContext
from symphony.bdk.core.activity.form import FormReplyActivity, FormReplyContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.message.model import Message
from symphony.bdk.core.symphony_bdk import SymphonyBdk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MessageML form template — sent when user types /feedback
FEEDBACK_FORM = """<messageML>
  <h2>Feedback Form</h2>
  <form id="feedback-form">
    <text-field name="name" placeholder="Your name..." required="true"/>
    <textarea name="feedback" placeholder="Share your feedback..."/>
    <select name="rating">
      <option value="5">⭐⭐⭐⭐⭐ Excellent</option>
      <option value="4">⭐⭐⭐⭐ Good</option>
      <option value="3">⭐⭐⭐ Average</option>
      <option value="2">⭐⭐ Poor</option>
      <option value="1">⭐ Terrible</option>
    </select>
    <button name="submit" type="action">Submit Feedback</button>
    <button type="reset">Clear</button>
  </form>
</messageML>"""


class FeedbackFormHandler(FormReplyActivity):
    """Handle submissions of the feedback-form."""

    def __init__(self, messages):
        self._messages = messages

    def matches(self, context: FormReplyContext) -> bool:
        return (
            context.form_id == "feedback-form"
            and context.get_form_value("action") == "submit"
        )

    async def on_activity(self, context: FormReplyContext):
        name = context.get_form_value("name")
        feedback = context.get_form_value("feedback")
        rating = context.get_form_value("rating")

        logger.info("Feedback received: name=%s, rating=%s", name, rating)

        await self._messages.send_message(
            context.source_event.stream.stream_id,
            f"<messageML>Thanks, <b>{name}</b>! "
            f"Rating: {'⭐' * int(rating)}<br/>"
            f"Feedback: <i>{feedback}</i></messageML>",
        )


async def main():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        activities = bdk.activities()
        messages = bdk.messages()

        # Slash command to send the form
        @activities.slash("/feedback", True, "Open the feedback form")
        async def send_form(ctx: CommandContext):
            await messages.send_message(ctx.stream_id, Message(content=FEEDBACK_FORM))

        # Register form handler
        activities.register(FeedbackFormHandler(messages))

        logger.info("Form bot started. Use /feedback to open the form.")
        await bdk.datafeed().start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Form bot stopped.")
