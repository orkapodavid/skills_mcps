---
name: Symphony BDK Python Agent
description: This skill should be used when the user asks to "build a Symphony bot", "send a message on Symphony", "create slash commands for Symphony", "configure BDK config.yaml", "implement a datafeed listener", "handle Symphony form submissions", "search Symphony messages or users", "build MCP tools backed by Symphony BDK", or needs guidance on symphony-bdk-python project setup, authentication, services API, or activity patterns.
version: 0.2.0
---

# Symphony BDK Python Agent Skill

Build bots and tool wrappers using the FINOS `symphony-bdk-python` SDK. This skill covers project bootstrap, configuration, chat-native bot patterns (slash commands, forms, datafeed listeners), and tool/API wrapper layers suitable for MCP integration.

## Quick-Start Checklist

1. **Pick interaction model**
   - *Chat-native bot* — implement Activities (slash commands, forms) and run the Datafeed loop.
   - *Tool/API wrapper* — build a thin "tools" layer that calls BDK services (Message, Stream, User, etc.).

2. **Install the SDK**
   - `pip install symphony-bdk-python>=2.0.0` or add to `pyproject.toml` / `requirements.txt`.

3. **Create configuration**
   - Place `config.yaml` in `~/.symphony/` for local dev (see `examples/config.yaml`).
   - Detailed config reference → `references/configuration.md`.

4. **Create a BDK session**
   - Always use `async with SymphonyBdk(config) as bdk:`.

5. **Access services**
   - `bdk.messages()` → send / search / update messages.
   - `bdk.streams()` → room / IM stream operations.
   - `bdk.users()` → user lookup.
   - `bdk.connections()`, `bdk.signals()`, `bdk.presence()`, `bdk.health()` → additional services.
   - Full service reference → `references/services-api.md`.

6. **Register activities** (chat-native bots only)
   - Register via `bdk.activities().register(...)` or `@bdk.activities().slash(...)`.
   - Start listening: `await bdk.datafeed().start()`.
   - Activity patterns → `references/activity-api.md`.

## Canonical Code Patterns

### Pattern A — Minimal "send a message" script

Use for one-off sends or when implementing an MCP-style tool handler.

```python
import asyncio
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.message.model import Message
from symphony.bdk.core.symphony_bdk import SymphonyBdk

async def main():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    async with SymphonyBdk(config) as bdk:
        await bdk.messages().send_message(
            "<STREAM_ID>",
            Message(content="<messageML>Hello</messageML>")
        )

asyncio.run(main())
```

### Pattern B — Slash command (decorator style)

Use when the bot responds to `/command` in Symphony chats.

```python
import asyncio
from symphony.bdk.core.activity.command import CommandContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk

async def main():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    async with SymphonyBdk(config) as bdk:
        activities = bdk.activities()
        messages = bdk.messages()

        @activities.slash("/hello", True, "Say hello")
        async def hello(ctx: CommandContext):
            await messages.send_message(
                ctx.stream_id, "<messageML>Hello!</messageML>"
            )

        await bdk.datafeed().start()

asyncio.run(main())
```

### Pattern C — Tools layer wrapper (MCP integration)

Create a class whose methods map 1:1 to tool calls. See `scripts/mcp_tool_skeleton.py` for a complete skeleton.

```python
from symphony.bdk.core.service.message.model import Message

class SymphonyTools:
    def __init__(self, bdk):
        self._messages = bdk.messages()

    async def send_message(self, stream_id: str, message_ml: str) -> None:
        await self._messages.send_message(
            stream_id, Message(content=message_ml)
        )
```

### Pattern D — RealTimeEventListener (datafeed subscriber)

Use to react to any real-time event (messages, room joins, etc.).

```python
import asyncio
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener

class MyListener(RealTimeEventListener):
    def __init__(self, message_service):
        self._messages = message_service

    async def on_message_sent(self, initiator, event):
        await self._messages.send_message(
            event.message.stream.stream_id,
            f"<messageML>Hello, {initiator.user.display_name}!</messageML>"
        )

async def main():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    async with SymphonyBdk(config) as bdk:
        bdk.datafeed().subscribe(MyListener(bdk.messages()))
        await bdk.datafeed().start()

asyncio.run(main())
```

### Pattern E — Form Activity (Elements form handler)

Use to handle form submissions from Symphony Elements.

```python
from symphony.bdk.core.activity.form import FormReplyActivity, FormReplyContext

class HelloFormActivity(FormReplyActivity):
    def __init__(self, messages):
        self._messages = messages

    def matches(self, context: FormReplyContext) -> bool:
        return (context.form_id == "hello-form"
                and context.get_form_value("action") == "submit")

    async def on_activity(self, context: FormReplyContext):
        name = context.get_form_value("name")
        await self._messages.send_message(
            context.source_event.stream.stream_id,
            f"<messageML>Hello, {name}!</messageML>"
        )
```

## Implementation Guidance

### MessageML & Elements
- Wrap chat outputs in `<messageML>...</messageML>`.
- Escape user-provided strings to avoid breaking XML.
- For interactive forms (text fields, dropdowns, checkboxes, buttons, tables), see `references/elements-messageml.md`.

### Async Correctness
- Activity callbacks **must be `async`**.
- Avoid `asyncio.run()` inside already-running event loops (common when embedding).
- For non-blocking datafeed handlers, wrap logic in `asyncio.create_task()`.

### Configuration (common failure points)
- Ensure **pod / agent / keyManager / sessionAuth** hosts match the target environment.
- Private key paths must be absolute and readable at runtime.
- Use datafeed `version: v2` (default) unless v1 is required.
- See `references/configuration.md` for the full config structure.

### Secrets and Safety
- Never log or return session tokens / key manager tokens.
- For tool wrappers: validate and sanitize inputs (`stream_id`, `user_id`, room identifiers).
- Add allow-lists for rooms the bot may post into (enterprise controls).

## Bundled Resources

### scripts/
- **`mcp_tool_skeleton.py`** — BDK-backed tools layer skeleton with message, stream, user, and health methods.
- **`bot_slash_command_skeleton.py`** — Runnable bot with `/hello` and `/help` commands plus argument parsing.

### references/
- **`links.md`** — Curated authoritative links to all FINOS BDK documentation pages.
- **`tool_surface.md`** — Suggested MCP tool surface: messaging, streams, users, connections, signals, health.
- **`configuration.md`** — Complete config.yaml structure, loading methods, SSL/proxy/retry settings.
- **`activity-api.md`** — Activity API deep-dive: CommandActivity, slash commands, forms, RealTimeEventListener, concurrency.
- **`services-api.md`** — All BDK service APIs: Message, Stream, User, Connection, Signal, Presence, Session, Health.
- **`elements-messageml.md`** — MessageML & Elements: tables, forms, buttons, text fields, dropdowns, checkboxes, radios, date/time pickers, and Python input capture.

### examples/
- **`config.yaml`** — Annotated minimal configuration template ready to copy and edit.
- **`realtime_listener_bot.py`** — Complete RealTimeEventListener bot.
- **`form_activity_bot.py`** — Complete form-handling bot with Elements form.
