# Activity API — Complete Reference

Every activity class, decorator, and context object from the `symphony-bdk-python` activity layer, extracted from
source code at [`symphony/bdk/core/activity/`](https://github.com/finos/symphony-bdk-python/tree/main/symphony/bdk/core/activity).

---

## ActivityRegistry — `bdk.activities()`

Source: `symphony/bdk/core/activity/registry.py`

The `ActivityRegistry` is itself a `RealTimeEventListener`. It dispatches real-time events to registered activities.

### Methods

| Method | Signature | Description |
|---|---|---|
| `register` | `(activity: AbstractActivity)` | Register an activity instance. If a matching activity already exists, it is replaced. |
| `slash` | `(command: str, mention_bot: bool = True, description: str = "")` | Decorator to register a slash command callback. |
| `activity_list` | property → `List[AbstractActivity]` | List of all registered activities (used by HelpCommand). |

### Events handled

The registry listens for three event types and dispatches to matching activities:

| Event | Source Event Type | Activity Type Dispatched |
|---|---|---|
| `on_message_sent` | `V4MessageSent` | `CommandActivity` (including `SlashCommandActivity`) |
| `on_symphony_elements_action` | `V4SymphonyElementsAction` | `FormReplyActivity` |
| `on_user_joined_room` | `V4UserJoinedRoom` | `UserJoinedRoomActivity` |

---

## CommandContext

Source: `symphony/bdk/core/activity/command.py`

Context object provided to all `CommandActivity.on_activity()` callbacks.

### Properties

| Property | Type | Description |
|---|---|---|
| `message_id` | `str` | ID of the triggering message |
| `stream_id` | `str` | Stream (conversation) ID where the message was sent |
| `text_content` | `str` | Parsed text content of the message (stripped of tags) |
| `bot_display_name` | `str` | The bot's display name |
| `bot_user_id` | `int` | The bot's user ID |
| `arguments` | `Arguments` | Parsed arguments (populated for slash commands with patterns) |
| `initiator` | `V4Initiator` | Info about the user who sent the message (`initiator.user.display_name`, `.user_id`) |
| `source_event` | `V4MessageSent` | Full raw event object |

---

## Arguments

Source: `symphony/bdk/core/activity/parsing/arguments.py`

Populated when a slash command with argument patterns matches. Access via `context.arguments`.

### Methods

| Method | Signature | Description |
|---|---|---|
| `get` | `(key: str)` | Get raw argument value (can be `str`, `Hashtag`, `Cashtag`, or `Mention`). |
| `get_string` | `(key: str) → str` | Get string argument. Returns `None` if not a plain string. |
| `get_as_string` | `(key: str) → str` | Get any argument as string (calls `.text` on non-string types). |
| `get_hashtag` | `(key: str) → Hashtag` | Get `#hashtag` argument. Returns `None` if not a Hashtag. |
| `get_cashtag` | `(key: str) → Cashtag` | Get `$cashtag` argument. Returns `None` if not a Cashtag. |
| `get_mention` | `(key: str) → Mention` | Get `@mention` argument. Returns `None` if not a Mention. |
| `get_argument_names` | `() → KeysView` | List all argument names. |

### Mention object properties

| Property | Description |
|---|---|
| `mention.user_id` | User ID of the mentioned user |
| `mention.user_display_name` | Display name of the mentioned user |

---

## CommandActivity (subclass approach)

Source: `symphony/bdk/core/activity/command.py`

Base class for any message-triggered activity. Implement `matches()` and `on_activity()`.

```python
from symphony.bdk.core.activity.command import CommandActivity, CommandContext
from symphony.bdk.core.service.message.message_service import MessageService

class HelloCommandActivity(CommandActivity):
    def __init__(self, messages: MessageService):
        self._messages = messages
        super().__init__()

    def matches(self, context: CommandContext) -> bool:
        return context.text_content.startswith(
            "@" + context.bot_display_name + " /hello"
        )

    async def on_activity(self, context: CommandContext):
        await self._messages.send_message(
            context.stream_id, "<messageML>Hello, World!</messageML>"
        )
```

Register and start:

```python
bdk.activities().register(HelloCommandActivity(bdk.messages()))
await bdk.datafeed().start()
```

---

## SlashCommandActivity — Decorator Style

The simplest way to define a command. The decorator wraps the callback in a `SlashCommandActivity`.

### Basic slash command

```python
@activities.slash("/hello")
async def on_hello(context: CommandContext):
    await messages.send_message(
        context.stream_id, "<messageML>Hello, World!</messageML>"
    )
```

### With bot mention and description

```python
@activities.slash("/hello", True, "Say hello to the bot")
async def on_hello(context: CommandContext):
    name = context.initiator.user.display_name
    await messages.send_message(
        context.stream_id, f"<messageML>Hello, {name}!</messageML>"
    )
```

### Parameters

| Parameter | Default | Description |
|---|---|---|
| `command` | (required) | Command pattern, e.g. `"/hello"` or `"/buy {ticker} {qty}"` |
| `mention_bot` | `True` | If `True`, user must `@mention` the bot to trigger |
| `description` | `""` | Description shown in `/help` output |

---

## Slash Command Arguments

### Argument patterns

Define arguments in the command string using `{braces}`:

| Pattern | User Types | `context.arguments` contains |
|---|---|---|
| `/buy {ticker}` | `/buy AAPL` | `get_string("ticker")` → `"AAPL"` |
| `/echo {first} {second}` | `/echo hello world` | `get_string("first")` → `"hello"`, `get_string("second")` → `"world"` |
| `/find {#tag}` | `/find #urgent` | `get_hashtag("tag")` → `Hashtag(value="urgent")` |
| `/price {$symbol}` | `/price $GOOG` | `get_cashtag("symbol")` → `Cashtag(value="GOOG")` |
| `/greet {@user}` | `/greet @John` | `get_mention("user")` → `Mention(user_id=..., user_display_name="John")` |

### Full example from official repo

```python
@activities.slash("/echo {@mention_argument}")
async def on_echo_mention(context: CommandContext):
    mentioned_user = context.arguments.get_mention("mention_argument")
    message = (
        f"Mentioned user: {mentioned_user.user_display_name}, "
        f"id: {mentioned_user.user_id}"
    )
    await messages.send_message(
        context.stream_id, f"<messageML>{message}</messageML>"
    )

@activities.slash("/echo {#hashtag_argument}")
async def on_echo_hashtag(context: CommandContext):
    hashtag = context.arguments.get_hashtag("hashtag_argument")
    await messages.send_message(
        context.stream_id, f"<messageML>Hashtag: {hashtag.value}</messageML>"
    )

@activities.slash("/echo {$cashtag_argument}")
async def on_echo_cashtag(context: CommandContext):
    cashtag = context.arguments.get_cashtag("cashtag_argument")
    await messages.send_message(
        context.stream_id, f"<messageML>Cashtag: {cashtag.value}</messageML>"
    )

@activities.slash("/echo {first_string_argument} {second_string_argument}")
async def on_echo_string(context: CommandContext):
    first = context.arguments.get_string("first_string_argument")
    second = context.arguments.get_as_string("second_string_argument")
    await messages.send_message(
        context.stream_id,
        f"<messageML>Args: {first} and {second}</messageML>"
    )
```

---

## HelpCommand (built-in)

Source: `symphony/bdk/core/activity/help_command.py`

Auto-generates a `/help` response listing all registered slash commands with their descriptions.

```python
from symphony.bdk.core.activity.help_command import HelpCommand

bdk.activities().register(HelpCommand(bdk))
```

Triggered by `@bot /help`. Outputs an HTML list of all registered commands.

---

## FormReplyActivity

Source: `symphony/bdk/core/activity/form.py`

Triggered when a user submits a Symphony Elements form.

### FormReplyContext

| Property | Type | Description |
|---|---|---|
| `form_id` | `str` | The `id` attribute of the `<form>` element |
| `form_values` | `dict` | All submitted form values |
| `initiator` | `V4Initiator` | User who submitted the form |
| `source_event` | `V4SymphonyElementsAction` | Full raw event |

| Method | Signature | Description |
|---|---|---|
| `get_form_value` | `(key: str) → str` | Get a submitted form field value by name. |

> **Note:** The stream ID is at `context.source_event.stream.stream_id` (not directly on context).

### Complete example from official repo

```python
from symphony.bdk.core.activity.command import CommandActivity, CommandContext
from symphony.bdk.core.activity.form import FormReplyActivity, FormReplyContext
from symphony.bdk.core.service.message.message_service import MessageService

# Step 1: Command sends a form
class SlashGifCommandActivity(CommandActivity):
    def __init__(self, messages: MessageService):
        self._messages = messages

    def matches(self, context: CommandContext) -> bool:
        return context.text_content.startswith(
            "@" + context.bot_display_name + " /gif"
        )

    async def on_activity(self, context: CommandContext):
        form_ml = """<messageML>
          <form id="gif-category-form">
            <text-field name="category" placeholder="Enter category..."/>
            <button name="action" type="action" value="submit">Submit</button>
          </form>
        </messageML>"""
        await self._messages.send_message(context.stream_id, form_ml)

# Step 2: Handler processes form submission
class ReplyFormReplyActivity(FormReplyActivity):
    def __init__(self, messages: MessageService):
        self._messages = messages

    def matches(self, context: FormReplyContext) -> bool:
        return (
            context.form_id == "gif-category-form"
            and context.get_form_value("action") == "submit"
            and context.get_form_value("category")
        )

    async def on_activity(self, context: FormReplyContext):
        category = context.get_form_value("category")
        await self._messages.send_message(
            context.source_event.stream.stream_id,
            f"<messageML>Category: {category}</messageML>",
        )

# Register both
bdk.activities().register(SlashGifCommandActivity(bdk.messages()))
bdk.activities().register(ReplyFormReplyActivity(bdk.messages()))
await bdk.datafeed().start()
```

---

## UserJoinedRoomActivity

Source: `symphony/bdk/core/activity/user_joined_room.py`

Triggered when a user joins a room.

### UserJoinedRoomContext

| Property | Type | Description |
|---|---|---|
| `stream_id` | `str` | Room stream ID |
| `user_id` | `int` | ID of the user who joined |
| `initiator` | `V4Initiator` | User who added the member (may differ from joined user) |
| `source_event` | `V4UserJoinedRoom` | Full raw event |

### Example from official repo

```python
from symphony.bdk.core.activity.user_joined_room import (
    UserJoinedRoomActivity,
    UserJoinedRoomContext,
)
from symphony.bdk.core.service.message.message_service import MessageService

class JoinRoomActivity(UserJoinedRoomActivity):
    def __init__(self, messages: MessageService):
        self._messages = messages
        super().__init__()

    def matches(self, context: UserJoinedRoomContext) -> bool:
        return True  # match all room joins

    async def on_activity(self, context: UserJoinedRoomContext):
        await self._messages.send_message(
            context.stream_id, "<messageML>Welcome to the room</messageML>"
        )

bdk.activities().register(JoinRoomActivity(bdk.messages()))
await bdk.datafeed().start()
```

---

## RealTimeEventListener (raw datafeed)

Source: `symphony/bdk/core/service/datafeed/real_time_event_listener.py`

Subscribe directly to datafeed events without the Activity abstraction. Use when processing events
that don't have a corresponding Activity class, or when custom event routing is needed.

### All listener methods

| Method | Event Type | Description |
|---|---|---|
| `on_message_sent` | `V4MessageSent` | Message received in any stream |
| `on_message_suppressed` | `V4MessageSuppressed` | Message deleted |
| `on_symphony_elements_action` | `V4SymphonyElementsAction` | Form submission |
| `on_shared_post` | `V4SharedPost` | Message shared/forwarded |
| `on_im_created` | `V4InstantMessageCreated` | IM stream created |
| `on_room_created` | `V4RoomCreated` | Room created |
| `on_room_updated` | `V4RoomUpdated` | Room attributes changed |
| `on_room_deactivated` | `V4RoomDeactivated` | Room deactivated |
| `on_room_reactivated` | `V4RoomReactivated` | Room reactivated |
| `on_user_joined_room` | `V4UserJoinedRoom` | User added to room |
| `on_user_left_room` | `V4UserLeftRoom` | User removed from room |
| `on_room_member_promoted_to_owner` | `V4RoomMemberPromotedToOwner` | User promoted to room owner |
| `on_room_member_demoted_from_owner` | `V4RoomMemberDemotedFromOwner` | User demoted from room owner |
| `on_connection_requested` | `V4ConnectionRequested` | Connection request received |
| `on_connection_accepted` | `V4ConnectionAccepted` | Connection request accepted |

### Example from official repo

```python
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent

class RealTimeEventListenerImpl(RealTimeEventListener):
    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        logging.debug("Received event: %s", event)

bdk.datafeed().subscribe(RealTimeEventListenerImpl())
await bdk.datafeed().start()
```

### Subscribe / Unsubscribe

```python
listener = RealTimeEventListenerImpl()
bdk.datafeed().subscribe(listener)

# Later, to unsubscribe:
bdk.datafeed().unsubscribe(listener)
```

---

## Concurrency Patterns

### Default behavior

For events received from one datafeed read:
1. For a given event → listener methods run **concurrently across** different listener instances.
2. For a given listener → methods run **concurrently across** different events.
3. The loop waits for all tasks to complete before the next read.

### Non-blocking handlers

To prevent slow handlers from blocking the loop:

```python
import asyncio

class FastListener(RealTimeEventListener):
    async def on_message_sent(self, initiator, event):
        asyncio.create_task(self._handle(initiator, event))

    async def _handle(self, initiator, event):
        # slow processing here
        pass
```

> **Important:** All listeners must use `create_task` for this to be effective.

---

## Datafeed Configuration

### Version

```yaml
datafeed:
  version: v2  # default; v1 only if pod requires it
```

### Retry

```yaml
datafeed:
  retry:
    maxAttempts: 6   # -1 for infinite
    initialIntervalMillis: 2000
    multiplier: 1.5
    maxIntervalMillis: 10000
```

### Logging context

A `ContextVar` is set during event processing:

```python
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import event_listener_context

context_id = event_listener_context.get("")  # "{task_name}/{event_id}/{listener_id}"
```
