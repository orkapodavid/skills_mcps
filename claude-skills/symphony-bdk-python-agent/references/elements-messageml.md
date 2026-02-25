# Symphony Elements & MessageML — Complete Reference

How to create interactive UI components (forms, buttons, tables, dropdowns, etc.) in Symphony messages
and capture user inputs in Python. All UI is defined in **MessageML** — an XML-based markup sent via
`send_message()`.

Official docs:
- [MessageML overview](https://docs.developers.symphony.com/building-bots-on-symphony/messages/overview-of-messageml)
- [Elements Interactive Forms](https://docs.developers.symphony.com/building-bots-on-symphony/messages/overview-of-messageml/symphony-elements-1)
- [Tables](https://docs.developers.symphony.com/building-bots-on-symphony/messages/overview-of-messageml/messageml-basic-format-tags/tables)

---

## MessageML Basics

All messages are wrapped in `<messageML>` tags. MessageML is XML (XHTML subset), so all tags must be
properly closed. Self-closing tags use `/>`.

### Supported formatting tags

| Tag | Description |
|---|---|
| `<b>`, `<i>`, `<u>` | Bold, italic, underline |
| `<br/>` | Line break (self-closing!) |
| `<p>` | Paragraph |
| `<h1>` – `<h6>` | Headings |
| `<ul>`, `<ol>`, `<li>` | Lists |
| `<code>` | Inline code |
| `<pre>` | Preformatted block |
| `<a href="url">` | Hyperlink |
| `<hr/>` | Horizontal rule |
| `<div>` | Content grouping |

### Special tags

| Tag | Description |
|---|---|
| `<mention uid="12345"/>` | @mention a user by numeric ID |
| `<mention email="user@company.com"/>` | @mention a user by email |
| `<hash tag="mytag"/>` | #hashtag |
| `<cash tag="AAPL"/>` | $cashtag |
| `<emoji shortcode="thumbsup"/>` | Emoji |
| `<card>` | Card with `<header>` and `<body>` |

---

## Mentions & Tagging

### @Mentioning users in outgoing messages

Use the `<mention>` tag to @mention a user. Two forms are supported:

```xml
<!-- By user ID (preferred — always resolves) -->
<messageML>Hello <mention uid="13056700580915"/>! Please review this.</messageML>

<!-- By email address -->
<messageML>Hello <mention email="alice@company.com"/>! Please review this.</messageML>
```

### Building mentions dynamically in Python

```python
# Mention a specific user by ID
user_id = 13056700580915
await bdk.messages().send_message(
    stream_id,
    f'<messageML>Hey <mention uid="{user_id}"/>, task assigned to you.</messageML>'
)
```

### Mention the user who sent a message (reply with mention)

```python
from symphony.bdk.core.activity.command import CommandContext

@activities.slash("/ack")
async def on_ack(context: CommandContext):
    sender_id = context.initiator.user.user_id
    await messages.send_message(
        context.stream_id,
        f'<messageML><mention uid="{sender_id}"/> — acknowledged! ✅</messageML>'
    )
```

### Mention multiple users

```python
user_ids = [13056700580915, 13056700580916, 13056700580917]
mentions = " ".join(f'<mention uid="{uid}"/>' for uid in user_ids)
await bdk.messages().send_message(
    stream_id,
    f"<messageML>Attention: {mentions} — meeting in 5 minutes.</messageML>"
)
```

---

## Responding Only When the Bot Is @Mentioned

### Approach 1: Slash commands with `mention_bot=True` (recommended)

The simplest approach. Set `mention_bot=True` (the default) so the command only fires
when the user @mentions the bot:

```python
# User must type: @BotName /status
@activities.slash("/status", True, "Show status")
async def on_status(context: CommandContext):
    await messages.send_message(context.stream_id, "<messageML>All systems go</messageML>")

# mention_bot=False → fires without @mention (e.g., "/status" alone)
@activities.slash("/help", False, "Show help")
async def on_help(context: CommandContext):
    ...
```

### Approach 2: Custom CommandActivity (respond to any @mention, not just slash commands)

For bots that should respond to **any** message where the bot is @mentioned (not just
slash commands), subclass `CommandActivity` and check `text_content` for the bot's display name:

```python
from symphony.bdk.core.activity.command import CommandActivity, CommandContext

class MentionOnlyActivity(CommandActivity):
    """Responds only when the bot is @mentioned in a message."""

    def __init__(self, messages):
        self._messages = messages
        super().__init__()

    def matches(self, context: CommandContext) -> bool:
        # Check if the bot's display name appears in the message text
        # (Symphony prefixes mentions with @)
        return f"@{context.bot_display_name}" in context.text_content

    async def on_activity(self, context: CommandContext):
        # Extract the text after the @mention
        text = context.text_content
        mention_prefix = f"@{context.bot_display_name}"
        user_message = text[text.index(mention_prefix) + len(mention_prefix):].strip()

        await self._messages.send_message(
            context.stream_id,
            f'<messageML>You said: "{user_message}"</messageML>'
        )

# Register
bdk.activities().register(MentionOnlyActivity(bdk.messages()))
await bdk.datafeed().start()
```

### Approach 3: RealTimeEventListener with mention filtering

For low-level control, filter `on_message_sent` events by checking if the bot's user ID
is in the message's mentions:

```python
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.service.message.message_parser import get_text_content_from_message

class MentionFilterListener(RealTimeEventListener):
    def __init__(self, bdk):
        self._messages = bdk.messages()
        self._bot_user_id = None

    async def on_message_sent(self, initiator, event):
        # Lazy-load bot user ID
        if self._bot_user_id is None:
            session = await self._messages._session_service.get_session()
            self._bot_user_id = session.id

        # Check if bot is mentioned in the message
        message = event.message
        if not self._is_bot_mentioned(message):
            return  # Ignore messages where bot is not tagged

        text = get_text_content_from_message(message)
        await self._messages.send_message(
            message.stream.stream_id,
            f"<messageML>I was mentioned! Message: {text}</messageML>"
        )

    def _is_bot_mentioned(self, message) -> bool:
        """Check if the bot's user ID appears in the message's user mentions."""
        if not hasattr(message, 'user_mentions') or not message.user_mentions:
            # Fallback: check text content for @BotName
            try:
                text = get_text_content_from_message(message)
                return f"@{self._bot_display_name}" in text
            except Exception:
                return False
        return any(m.id == self._bot_user_id for m in message.user_mentions)
```

> **Tip:** Approach 1 (slash commands with `mention_bot=True`) is the most reliable and
> simplest. Use Approach 2 or 3 only when building conversational bots that respond to
> free-form @mentions rather than fixed commands.

### XML escaping

| Character | Escape |
|---|---|
| `<` | `&lt;` |
| `&` | `&amp;` |
| `"` | `&quot;` |
| `'` | `&apos;` |

---

## Tables

Tables are basic MessageML elements (not part of forms — they display data only, no user input).

### Tags

| Tag | Description | Optional Attributes |
|---|---|---|
| `<table>` | Table container | `class` |
| `<thead>` | Table header section | `class` |
| `<tbody>` | Table body section | `class` |
| `<tfoot>` | Table footer section | `class` |
| `<tr>` | Table row | `class` |
| `<td>` | Table cell | `class`, `rowspan`, `colspan` |

### Example — Data table

```xml
<messageML>
  <h2>Q4 Results</h2>
  <table>
    <thead>
      <tr>
        <td>Region</td>
        <td>Revenue</td>
        <td>Growth</td>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>APAC</td>
        <td>$12.5M</td>
        <td>+15%</td>
      </tr>
      <tr>
        <td>EMEA</td>
        <td>$8.2M</td>
        <td>+7%</td>
      </tr>
    </tbody>
  </table>
</messageML>
```

### Send a table from Python

```python
table_ml = """<messageML>
  <table>
    <thead><tr><td>Name</td><td>Status</td></tr></thead>
    <tbody>
      <tr><td>Server A</td><td>Online</td></tr>
      <tr><td>Server B</td><td>Offline</td></tr>
    </tbody>
  </table>
</messageML>"""
await bdk.messages().send_message(stream_id, table_ml)
```

### Dynamic table from data

```python
def build_table(headers: list[str], rows: list[list[str]]) -> str:
    header_cells = "".join(f"<td>{h}</td>" for h in headers)
    body_rows = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
        for row in rows
    )
    return f"""<messageML>
      <table>
        <thead><tr>{header_cells}</tr></thead>
        <tbody>{body_rows}</tbody>
      </table>
    </messageML>"""

await bdk.messages().send_message(
    stream_id,
    build_table(["Ticker", "Price"], [["AAPL", "182.52"], ["GOOG", "141.80"]])
)
```

---

## Forms (Interactive Elements)

Forms are the container for all interactive elements. A form **must** contain at least one
action-type `<button>`.

### `<form>` tag

| Attribute | Type | Required | Description |
|---|---|---|---|
| `id` | String | Yes | Unique form identifier — used in `FormReplyContext.form_id` to match submissions |
| `multi-submit` | String | No | `"reset"` = re-enable form with defaults after submit; `"no-reset"` = keep submitted values. If omitted, form disables after one submit. |

### Form behavior

1. Bot sends a message containing a `<form>` with elements and buttons
2. User fills in the form and clicks an action button
3. Symphony sends a `SYMPHONY_ELEMENTS_ACTION` event via datafeed
4. The `FormReplyActivity` (or `RealTimeEventListener.on_symphony_elements_action`) handles it
5. The bot reads submitted values via `context.get_form_value("field_name")`

---

## Buttons

Every form must contain at least one action button.

### `<button>` attributes

| Attribute | Type | Required | Description |
|---|---|---|---|
| `name` | String | Yes | Identifies the button in the payload. The button `name` becomes the `action` field value in the datafeed. |
| `type` | String | No (default: `action`) | `"action"` = submits form data; `"reset"` = resets form to defaults |
| `class` | String | No (default: `primary`) | Visual style: `primary`, `secondary`, `destructive`, `primary-link`, `tertiary`, `destructive-link` |
| `icon` | String | No | Icon name from the [UI Toolkit icon set](https://docs.developers.symphony.com/bots/messages/overview-of-messageml/symphony-elements-1/buttons/icon-set-for-buttons) |
| `formnovalidate` | Boolean | No | If `true`, submit bypasses required-field and regex validation |

### Example

```xml
<button name="approve" type="action" class="primary">Approve</button>
<button name="reject" type="action" class="destructive">Reject</button>
<button type="reset" class="secondary">Clear</button>
```

---

## Text Field

Single-line text input.

### `<text-field>` attributes

| Attribute | Type | Required | Description |
|---|---|---|---|
| `name` | String | Yes | Field identifier |
| `placeholder` | String | No | Hint text shown when empty |
| `required` | Boolean | No | Must be filled before submit |
| `masked` | Boolean | No | Password-style masked input |
| `maxlength` | Integer | No | Maximum character count |
| `minlength` | Integer | No | Minimum character count |
| `pattern` | String | No | Regex for input validation |
| `pattern-error-message` | String | Required if `pattern` set | Error shown on invalid input |
| `label` | String | No | Label displayed above field |
| `title` | String | No | Tooltip text (max 256 chars) |
| `auto-submit` | Boolean | No | Submit form on Enter key |

### Example

```xml
<text-field name="email" required="true" placeholder="user@example.com"
            pattern="^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"
            pattern-error-message="Enter a valid email address"
            label="Email Address"/>
```

---

## Text Area

Multi-line text input.

### `<textarea>` attributes

| Attribute | Type | Required | Description |
|---|---|---|---|
| `name` | String | Yes | Field identifier |
| `placeholder` | String | No | Hint text |
| `required` | Boolean | No | Must be filled before submit |
| `maxlength` | Integer | No | Maximum characters |
| `minlength` | Integer | No | Minimum characters |
| `label` | String | No | Label above field |
| `title` | String | No | Tooltip text |

### Example

```xml
<textarea name="comments" placeholder="Add your feedback here..."
          required="true" label="Comments"/>
```

---

## Dropdown Menu (Select)

Single or multi-select dropdown.

### `<select>` attributes

| Attribute | Type | Required | Description |
|---|---|---|---|
| `name` | String | Yes | Field identifier |
| `required` | Boolean | No | At least one option must be selected |
| `data-placeholder` | String | No | Placeholder text before selection |
| `multiple` | Boolean | No (default: `false`) | Allow multi-select |
| `min` | Integer | No (requires `multiple="true"`) | Minimum selections (≥ 2) |
| `max` | Integer | No (requires `multiple="true"`) | Maximum selections (≥ 2) |
| `label` | String | No | Label above dropdown |
| `auto-submit` | Boolean | No | Submit form on selection |

### `<option>` attributes

| Attribute | Type | Required | Description |
|---|---|---|---|
| `value` | String | Yes | Value sent in the payload |
| `selected` | Boolean | No | Pre-selected option |

### Example — Single select

```xml
<select name="priority" required="true" label="Priority">
  <option value="low">Low</option>
  <option value="medium" selected="true">Medium</option>
  <option value="high">High</option>
  <option value="critical">Critical</option>
</select>
```

### Example — Multi-select

```xml
<select name="assignees" multiple="true" min="1" max="3"
        data-placeholder="Choose assignees...">
  <option value="alice">Alice</option>
  <option value="bob">Bob</option>
  <option value="charlie">Charlie</option>
</select>
```

---

## Checkbox

Multiple-choice selection (independent toggles).

### `<checkbox>` attributes

| Attribute | Type | Required | Description |
|---|---|---|---|
| `name` | String | Yes | Field identifier |
| `value` | String | Yes | Value sent when checked |
| `checked` | Boolean | No | Pre-checked state |

### Example

```xml
<checkbox name="features" value="auth" checked="true">Authentication</checkbox>
<checkbox name="features" value="logging">Logging</checkbox>
<checkbox name="features" value="monitoring">Monitoring</checkbox>
```

> **Note:** Multiple checkboxes with the **same `name`** are grouped. The submitted value is an
> array of all checked values.

---

## Radio Buttons

Single-choice selection from a group.

### `<radio>` attributes

| Attribute | Type | Required | Description |
|---|---|---|---|
| `name` | String | Yes | Group name — radios with the same `name` form a group |
| `value` | String | Yes | Value sent when selected |
| `checked` | Boolean | No | Pre-selected state (only one per group) |

### Example

```xml
<radio name="urgency" value="low">Low</radio>
<radio name="urgency" value="medium" checked="true">Medium</radio>
<radio name="urgency" value="high">High</radio>
```

---

## Person Selector

User picker element for selecting Symphony users.

```xml
<person-selector name="approver" placeholder="Search for a user..."
                 required="true" label="Select approver"/>
```

---

## Date Picker

```xml
<date-selector name="due_date" label="Due Date" required="true"/>
```

---

## Time Picker

```xml
<time-selector name="meeting_time" label="Meeting Time"
               required="false" format="12-hours"/>
```

---

## Complete Form Example

```xml
<messageML>
  <h3>New Task</h3>
  <form id="task-form" multi-submit="reset">

    <text-field name="title" required="true"
                placeholder="Task title" label="Title"/>

    <textarea name="description"
              placeholder="Describe the task..." label="Description"/>

    <select name="priority" required="true" label="Priority">
      <option value="low">Low</option>
      <option value="medium" selected="true">Medium</option>
      <option value="high">High</option>
    </select>

    <radio name="type" value="bug">Bug</radio>
    <radio name="type" value="feature" checked="true">Feature</radio>
    <radio name="type" value="task">Task</radio>

    <checkbox name="labels" value="frontend">Frontend</checkbox>
    <checkbox name="labels" value="backend">Backend</checkbox>
    <checkbox name="labels" value="devops">DevOps</checkbox>

    <person-selector name="assignee" placeholder="Assign to..."
                     required="true" label="Assignee"/>

    <date-selector name="due_date" label="Due Date"/>

    <button name="create" type="action" class="primary">Create Task</button>
    <button type="reset" class="secondary">Clear</button>
  </form>
</messageML>
```

---

## Capturing User Inputs in Python

### Using FormReplyActivity (recommended)

```python
from symphony.bdk.core.activity.form import FormReplyActivity, FormReplyContext
from symphony.bdk.core.service.message.message_service import MessageService

class TaskFormHandler(FormReplyActivity):
    def __init__(self, messages: MessageService):
        self._messages = messages

    def matches(self, context: FormReplyContext) -> bool:
        return (
            context.form_id == "task-form"
            and context.get_form_value("action") == "create"
        )

    async def on_activity(self, context: FormReplyContext):
        title    = context.get_form_value("title")
        desc     = context.get_form_value("description")
        priority = context.get_form_value("priority")
        task_type = context.get_form_value("type")
        labels   = context.get_form_value("labels")    # list if multiple checkboxes
        assignee = context.get_form_value("assignee")
        due_date = context.get_form_value("due_date")

        reply = f"""<messageML>
          <b>Task Created</b><br/>
          Title: {title}<br/>
          Priority: {priority}<br/>
          Type: {task_type}<br/>
          Labels: {labels}<br/>
          Due: {due_date}
        </messageML>"""

        stream_id = context.source_event.stream.stream_id
        await self._messages.send_message(stream_id, reply)

# Register
bdk.activities().register(TaskFormHandler(bdk.messages()))
```

### FormReplyContext API

| Property / Method | Returns | Description |
|---|---|---|
| `context.form_id` | `str` | The `id` attribute of the `<form>` tag |
| `context.form_values` | `dict` | All submitted field values as a dictionary |
| `context.get_form_value("name")` | `str` or `list` | Get a single field value. Returns a list if multiple elements share the same `name`. |
| `context.initiator` | `V4Initiator` | User who submitted the form |
| `context.source_event` | `V4SymphonyElementsAction` | Full raw event |
| `context.source_event.stream.stream_id` | `str` | Stream ID where the form was sent |

### Which button was clicked?

The `name` attribute of the clicked button is available via:

```python
action = context.get_form_value("action")  # returns the button's name attribute value
```

> **Convention:** Use `name="action"` on buttons and check its value to determine which button
> was pressed. The button's text content is NOT submitted — only its `name` attribute.

### Using RealTimeEventListener (alternative)

```python
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener

class FormListener(RealTimeEventListener):
    async def on_symphony_elements_action(self, initiator, event):
        form_id = event.form_id
        values  = event.form_values  # dict of all form values
        stream  = event.stream.stream_id

        if form_id == "task-form":
            title = values.get("title")
            # process...
```

---

## Sending Forms Dynamically

### Send a form via slash command

```python
@activities.slash("/feedback", True, "Open feedback form")
async def on_feedback(context: CommandContext):
    form_ml = """<messageML>
      <form id="feedback-form">
        <h4>Feedback</h4>
        <select name="rating" label="Rating" required="true">
          <option value="1">⭐</option>
          <option value="2">⭐⭐</option>
          <option value="3">⭐⭐⭐</option>
          <option value="4">⭐⭐⭐⭐</option>
          <option value="5">⭐⭐⭐⭐⭐</option>
        </select>
        <textarea name="comments" placeholder="Any comments?" label="Comments"/>
        <button name="submit" type="action">Submit</button>
      </form>
    </messageML>"""
    await messages.send_message(context.stream_id, form_ml)
```

### Table inside a form

Tables can be placed inside forms to create data grids with action buttons:

```xml
<messageML>
  <form id="approval-form">
    <h4>Pending Approvals</h4>
    <table>
      <thead>
        <tr><td>Request</td><td>Amount</td><td>Status</td></tr>
      </thead>
      <tbody>
        <tr><td>Travel</td><td>$1,200</td><td>Pending</td></tr>
        <tr><td>Software</td><td>$500</td><td>Pending</td></tr>
      </tbody>
    </table>
    <button name="approve_all" type="action" class="primary">Approve All</button>
    <button name="reject_all" type="action" class="destructive">Reject All</button>
  </form>
</messageML>
```

---

## Cards (Expandable Messages)

Cards provide collapsible content sections (not interactive — for display only):

```xml
<messageML>
  <card>
    <header>Alert: Server Down</header>
    <body>
      <p>Server <b>prod-web-03</b> is unreachable since 14:30 UTC.</p>
      <table>
        <tr><td>Host</td><td>prod-web-03</td></tr>
        <tr><td>Last Ping</td><td>14:30 UTC</td></tr>
        <tr><td>Status</td><td>DOWN</td></tr>
      </table>
    </body>
  </card>
</messageML>
```

---

## Quick Reference — All Elements

| Element | Tag | Inside `<form>`? | User Input? |
|---|---|---|---|
| Text Field | `<text-field>` | Yes | Yes |
| Text Area | `<textarea>` | Yes | Yes |
| Dropdown | `<select>` + `<option>` | Yes | Yes |
| Checkbox | `<checkbox>` | Yes | Yes |
| Radio | `<radio>` | Yes | Yes |
| Button | `<button>` | Yes | Trigger |
| Person Selector | `<person-selector>` | Yes | Yes |
| Date Picker | `<date-selector>` | Yes | Yes |
| Time Picker | `<time-selector>` | Yes | Yes |
| Table | `<table>` | Both | No |
| Card | `<card>` | No | No |
| Image | `<img src="url"/>` | No | No |
| Emoji | `<emoji shortcode="..."/>` | Both | No |
