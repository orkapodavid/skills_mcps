# BDK Services API — Complete Reference

Every public method from the `symphony-bdk-python` service layer, extracted from source code at
[`symphony/bdk/core/service/`](https://github.com/finos/symphony-bdk-python/tree/main/symphony/bdk/core/service).

All methods are `async`. Access services from the `SymphonyBdk` entry point:

```python
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk

async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    async with SymphonyBdk(config) as bdk:
        messages = bdk.messages()
        streams  = bdk.streams()
        users    = bdk.users()
        # ... etc.
```

> **Async generators**: Methods prefixed with `list_all_*` / `search_all_*` return `AsyncGenerator`.
> Iterate with `async for item in await svc.list_all_*(...):`.

---

## MessageService — `bdk.messages()`

Source: `symphony/bdk/core/service/message/message_service.py` (548 lines)

### Send & Blast

| Method | Signature | Description |
|---|---|---|
| `send_message` | `(stream_id: str, message: Union[str, Message], data=None, version="", attachment=None)` | Send a message to a stream. `message` can be a plain MessageML string or a `Message` object with attachments. |
| `blast_message` | `(stream_ids: List[str], message: Union[str, Message], data=None, version="", attachment=None)` | Send the same message to multiple streams at once. |

#### Example — Send with attachments

```python
from symphony.bdk.core.service.message.model import Message

with open("report.pdf", "rb") as f1, open("chart.png", "rb") as f2:
    msg = Message(content="<messageML>See attached.</messageML>", attachments=[f1, f2])
    await bdk.messages().send_message(stream_id, msg)
```

#### Example — Send with attachment + preview

```python
with open("file.pdf", "rb") as attachment, open("preview.jpg", "rb") as preview:
    msg = Message(
        content="<messageML>Document</messageML>",
        attachments=[(attachment, preview)]  # tuple = (file, preview)
    )
    await bdk.messages().send_message(stream_id, msg)
```

#### Example — Blast to multiple streams

```python
await bdk.messages().blast_message(
    [stream_id_1, stream_id_2],
    "<messageML>Announcement!</messageML>"
)
```

### Update & Suppress

| Method | Signature | Description |
|---|---|---|
| `update_message` | `(stream_id: str, message_id: str, message: Union[str, Message], data=None, version="", silent=True)` | Update an existing message. The message must not be deleted. `silent=True` prevents a notification to users. |
| `suppress_message` | `(message_id: str) → MessageSuppressionResponse` | Suppress (delete) a message. |

#### Example — Update a message

```python
sent = await bdk.messages().send_message(stream_id, "Loading...")
await bdk.messages().update_message(
    stream_id, sent.message_id, "<messageML>Done! ✅</messageML>"
)
```

### Retrieve Messages

| Method | Signature | Description |
|---|---|---|
| `get_message` | `(message_id: str) → V4Message` | Get a single message by ID. |
| `list_messages` | `(stream_id: str, since: int = 0, skip: int = 0, limit: int = 50)` | List messages in a stream. `since` is a Unix timestamp (ms). |

### Search

| Method | Signature | Description |
|---|---|---|
| `search_messages` | `(query: MessageSearchQuery, sort_dir="desc", skip=0, limit=50)` | Search messages with pagination. |
| `search_all_messages` | `(query: MessageSearchQuery, sort_dir="desc", chunk_size=50, max_number=None) → AsyncGenerator` | Auto-paginating search returning all matching messages. |

#### Example — Search messages

```python
from symphony.bdk.gen.agent_model.message_search_query import MessageSearchQuery

query = MessageSearchQuery(text="quarterly report", stream_id=stream_id)
async for m in await bdk.messages().search_all_messages(query):
    print(m.message_id, m.message)
```

### Attachments

| Method | Signature | Description |
|---|---|---|
| `get_attachment` | `(stream_id: str, message_id: str, attachment_id: str) → bytes` | Download attachment body (base64-encoded bytes). |
| `list_attachments` | `(stream_id: str, since=None, to=None, limit=50, sort_dir="ASC") → List[StreamAttachmentItem]` | List attachments in a stream. `since`/`to` are timestamps (ms). |
| `get_attachment_types` | `() → List[str]` | List supported file extensions for attachments. |

### Message Metadata

| Method | Signature | Description |
|---|---|---|
| `get_message_status` | `(message_id: str) → MessageStatus` | Get read/delivery status of a message. |
| `list_message_receipts` | `(message_id: str) → MessageReceiptDetailResponse` | Fetch detailed receipt info (sent/delivered/read timestamps per user). |
| `get_message_relationships` | `(message_id: str) → MessageMetadataResponse` | Track forwards, replies, and form replies of a message. |

### Import

| Method | Signature | Description |
|---|---|---|
| `import_messages` | `(messages: List[V4ImportedMessage]) → List` | Import messages into Symphony (migration use case). |

#### Example — Import message with attachment

```python
import base64
from symphony.bdk.gen.agent_model.v4_imported_message import V4ImportedMessage
from symphony.bdk.gen.agent_model.v4_imported_message_attachment import V4ImportedMessageAttachment

content = base64.b64encode(b"symphony").decode("ascii")
attachment = V4ImportedMessageAttachment(filename="text.txt", content=content)
msg = V4ImportedMessage(
    intended_message_timestamp=1647353689268,
    intended_message_from_user_id=13056700580915,
    originating_system_id="fooChat",
    stream_id=stream_id,
    message="<messageML>Imported message</messageML>",
    attachments=[attachment],
)
await bdk.messages().import_messages([msg])
```

---

## StreamService — `bdk.streams()`

Source: `symphony/bdk/core/service/stream/stream_service.py` (508 lines)

### Create & Info

| Method | Signature | Description |
|---|---|---|
| `create_im` | `(user_id: int) → Stream` | Create a single-party IM (bot is auto-included). |
| `create_im_admin` | `(user_ids: [int]) → Stream` | Admin IM/MIM creation (caller NOT auto-included, ≥2 users required). |
| `create_room` | `(room_attributes: V3RoomAttributes) → V3RoomDetail` | Create a chatroom. If no attributes, defaults to private room. |
| `get_stream` | `(stream_id: str) → StreamAttributes` | Get stream info (type, members, attributes). |
| `get_room_info` | `(room_id: str) → V3RoomDetail` | Get room metadata. |
| `get_im_info` | `(im_id: str) → V1IMDetail` | Get IM details (StreamService only, not OBO). |

#### Example — Create a room

```python
from symphony.bdk.gen.pod_model.v3_room_attributes import V3RoomAttributes

room = await bdk.streams().create_room(
    V3RoomAttributes(name="New fancy room", description="test room")
)
```

### Update & Activate

| Method | Signature | Description |
|---|---|---|
| `update_room` | `(room_id: str, room_attributes: V3RoomAttributes) → V3RoomDetail` | Update room attributes. |
| `update_im` | `(im_id: str, im_attributes: V1IMAttributes) → V1IMDetail` | Update IM attributes (StreamService only). |
| `set_room_active` | `(room_id: str, active: bool) → V3RoomDetail` | Deactivate (`False`) or reactivate (`True`) a room. |
| `set_room_active_admin` | `(room_id: str, active: bool) → V3RoomDetail` | Admin version of de/reactivate room. |

### Membership

| Method | Signature | Description |
|---|---|---|
| `add_member_to_room` | `(user_id: int, room_id: str)` | Add a user to a room. |
| `remove_member_from_room` | `(user_id: int, room_id: str)` | Remove a user from a room. |
| `promote_user_to_room_owner` | `(user_id: int, room_id: str)` | Promote a user to room owner. |
| `demote_owner_to_room_participant` | `(user_id: int, room_id: str)` | Demote room owner to participant. |
| `list_room_members` | `(room_id: str) → V2MembershipList` | List members of a room. (in OboStreamService) |
| `list_all_stream_members` | `(stream_id: str, chunk_size=100, max_number=None) → AsyncGenerator[V2MemberInfo]` | Auto-paginating list of all stream members. |

#### Example — Membership operations

```python
streams = bdk.streams()
await streams.add_member_to_room(13056700579859, stream_id)
await streams.remove_member_from_room(13056700579859, stream_id)

async for member in await streams.list_all_stream_members(stream_id):
    print(member)
```

### Search & List

| Method | Signature | Description |
|---|---|---|
| `list_streams` | `(stream_filter: StreamFilter, skip=0, limit=50)` | List streams the user is a member of. |
| `list_all_streams` | `(stream_filter: StreamFilter, chunk_size=50, max_number=None) → AsyncGenerator` | Auto-paginating version. |
| `search_rooms` | `(query: V2RoomSearchCriteria, skip=0, limit=50, include_non_discoverable=False) → V3RoomSearchResults` | Search for rooms. |
| `search_all_rooms` | `(query: V2RoomSearchCriteria, chunk_size=50, max_number=None, include_non_discoverable=False) → AsyncGenerator` | Auto-paginating search. |
| `list_streams_admin` | `(stream_filter: V2AdminStreamFilter, skip=0, limit=50) → V2AdminStreamList` | List all streams across the enterprise (admin). |
| `list_all_streams_admin` | `(stream_filter: V2AdminStreamFilter, chunk_size=50, max_number=None) → AsyncGenerator[V2AdminStreamInfo]` | Auto-paginating admin version. |

#### Example — List streams by type

```python
from symphony.bdk.gen.pod_model.stream_filter import StreamFilter
from symphony.bdk.gen.pod_model.stream_type import StreamType

stream_filter = StreamFilter(
    stream_types=[StreamType(type="IM"), StreamType(type="ROOM")],
    include_inactive_streams=False,
)
async for s in await bdk.streams().list_all_streams(stream_filter):
    print(s)
```

### Share

| Method | Signature | Description |
|---|---|---|
| `share` | `(stream_id: str, content: ShareContent) → V4Message` | Share third-party content into a stream. |

---

## UserService — `bdk.users()`

Source: `symphony/bdk/core/service/user/user_service.py` (813 lines)

### Lookup

| Method | Signature | Description |
|---|---|---|
| `list_users_by_ids` | `(user_ids: [int], local=False, active=None) → V2UserList` | Look up users by their IDs. |
| `list_users_by_emails` | `(emails: [str], local=False, active=None) → V2UserList` | Look up users by email addresses. |
| `list_users_by_usernames` | `(usernames: [str], active=None) → V2UserList` | Look up users by usernames. |

#### Example — User lookup

```python
users = await bdk.users().list_users_by_ids([12987981103610])
print(users)
```

### Search

| Method | Signature | Description |
|---|---|---|
| `search_users` | `(query: UserSearchQuery, local=False, skip=0, limit=50)` | Search by name, email, etc. with optional filters (company, title, location). |
| `search_all_users` | `(query: UserSearchQuery, local=False, chunk_size=50, max_number=None) → AsyncGenerator` | Auto-paginating search. |

#### Example — Search with filter

```python
from symphony.bdk.gen.pod_model.user_search_filter import UserSearchFilter
from symphony.bdk.gen.pod_model.user_search_query import UserSearchQuery

query = UserSearchQuery(query="bot", filters=UserSearchFilter(company="Symphony"))
async for uid in await bdk.users().search_all_users(query, local=False):
    print(uid)
```

### Admin: User CRUD

| Method | Signature | Description |
|---|---|---|
| `get_user_detail` | `(user_id: int) → V2UserDetail` | Get detailed info for a user. |
| `list_user_details` | `(skip=0, limit=50) → V2UserList` | List all users in the pod. |
| `list_all_user_details` | `(chunk_size=50, max_number=None) → AsyncGenerator` | Auto-paginating list of all users. |
| `list_user_details_by_filter` | `(user_filter: UserFilter, skip=0, limit=50)` | Filter users by status, role, etc. |
| `list_all_user_details_by_filter` | `(user_filter: UserFilter, chunk_size=50, max_number=None) → AsyncGenerator` | Auto-paginating filtered list. |
| `create` | `(payload: V2UserCreate) → V2UserDetail` | Create a new user (admin). |
| `update` | `(user_id: int, payload: V2UserAttributes) → V2UserDetail` | Update user attributes (admin). |

#### Example — List users by filter

```python
from symphony.bdk.gen.pod_model.user_filter import UserFilter

async for u in await bdk.users().list_all_user_details_by_filter(
    user_filter=UserFilter(status="ENABLED", role="INDIVIDUAL"), max_number=100
):
    print(u.user_attributes.display_name)
```

### Admin: Roles & Status

| Method | Signature | Description |
|---|---|---|
| `add_role` | `(user_id: int, role_id: RoleId)` | Assign a role to a user. |
| `remove_role` | `(user_id: int, role_id: RoleId)` | Remove a role from a user. |
| `list_roles` | `() → List[RoleDetail]` | List all roles in the pod. |
| `get_status` | `(user_id: int) → UserStatus` | Get user's account status. |
| `update_status` | `(user_id: int, user_status: UserStatus)` | Update user's account status. |
| `suspend_user` | `(user_id: int, user_suspension: UserSuspension)` | Suspend or unsuspend a user. |
| `suspend` | `(user_id: int, reason=None, until=None)` | Convenience: suspend with reason and optional expiry timestamp (ms). |

### Admin: Avatar, Disclaimer, Delegates

| Method | Signature | Description |
|---|---|---|
| `get_avatar` | `(user_id: int) → List[Avatar]` | Get URLs of user's avatar images. |
| `update_avatar` | `(user_id: int, image: Union[str, bytes])` | Update avatar (base64-encoded string or bytes). |
| `get_disclaimer` | `(user_id: int) → Disclaimer` | Get disclaimer assigned to a user. |
| `add_disclaimer` | `(user_id: int, disclaimer_id: str)` | Assign a disclaimer. |
| `remove_disclaimer` | `(user_id: int)` | Unassign disclaimer from user. |
| `get_delegates` | `(user_id: int) → List` | Get delegates assigned to user. |
| `update_delegates` | `(user_id: int, delegate_user_id: int, action: DelegateActionEnum)` | Update delegates (add/remove). |

### Admin: Feature Entitlements

| Method | Signature | Description |
|---|---|---|
| `get_feature_entitlements` | `(user_id: int) → FeatureList` | Get feature entitlements of user. |
| `update_feature_entitlements` | `(user_id: int, features: [Feature])` | Update feature entitlements. |

### Followers / Following

| Method | Signature | Description |
|---|---|---|
| `follow_user` | `(follower_ids: [int], user_id: int)` | Make users follow a specific user. |
| `unfollow_user` | `(follower_ids: [int], user_id: int)` | Make users stop following a user. |
| `list_user_followers` | `(user_id: int, limit=100, before=None, after=None) → FollowersListResponse` | List followers of a user. |
| `list_all_user_followers` | `(user_id: int, chunk_size=100, max_number=None) → AsyncGenerator` | Auto-paginating followers list. |
| `list_users_following` | `(user_id: int, limit=100, before=None, after=None) → FollowingListResponse` | List users followed by a user. |
| `list_all_users_following` | `(user_id: int, chunk_size=100, max_number=None) → AsyncGenerator` | Auto-paginating following list. |

### Audit Trail

| Method | Signature | Description |
|---|---|---|
| `list_audit_trail` | `(start_timestamp: int, end_timestamp=None, initiator_id=None, role=None, limit=50, before=None, after=None)` | Audit trail of privileged user actions. |
| `list_all_audit_trail` | `(start_timestamp: int, end_timestamp=None, initiator_id=None, role=None, chunk_size=100, max_number=None) → AsyncGenerator` | Auto-paginating audit trail. |

---

## ConnectionService — `bdk.connections()`

Source: `symphony/bdk/core/service/connection/connection_service.py` (147 lines)

| Method | Signature | Description |
|---|---|---|
| `get_connection` | `(user_id: int) → UserConnection` | Check connection status with a user. |
| `list_connections` | `(status: ConnectionStatus = ALL, user_ids: [int] = None) → List[UserConnection]` | List connections. Status: `ALL`, `PENDING_INCOMING`, `PENDING_OUTGOING`, `ACCEPTED`, `REJECTED`. |
| `create_connection` | `(user_id: int) → UserConnection` | Send a connection request. |
| `accept_connection` | `(user_id: int) → UserConnection` | Accept a pending request. |
| `reject_connection` | `(user_id: int) → UserConnection` | Reject a pending request. |
| `remove_connection` | `(user_id: int) → None` | Remove an existing connection. |

#### Example — List all connections

```python
from symphony.bdk.core.service.connection.model.connection_status import ConnectionStatus

connections = await bdk.connections().list_connections(status=ConnectionStatus.ALL)
print(connections)
```

#### Import for ConnectionStatus

```python
from symphony.bdk.core.service.connection.model.connection_status import ConnectionStatus
# Values: ConnectionStatus.ALL, PENDING_INCOMING, PENDING_OUTGOING, ACCEPTED, REJECTED
```

---

## SignalService — `bdk.signals()`

Source: `symphony/bdk/core/service/signal/signal_service.py` (237 lines)

| Method | Signature | Description |
|---|---|---|
| `list_signals` | `(skip=0, limit=50) → SignalList` | List signals the user created or subscribed to. |
| `list_all_signals` | `(chunk_size=50, max_number=None) → AsyncGenerator[Signal]` | Auto-paginating list. |
| `get_signal` | `(signal_id: str) → Signal` | Get signal details by ID. |
| `create_signal` | `(signal: BaseSignal) → Signal` | Create a new signal. |
| `update_signal` | `(signal_id: str, signal: BaseSignal) → Signal` | Update an existing signal. |
| `delete_signal` | `(signal_id: str)` | Delete a signal. |
| `subscribe_users_to_signal` | `(signal_id: str, pushed: bool, user_ids: [int]) → ChannelSubscriptionResponse` | Subscribe users. `pushed=True` to push notifications. |
| `unsubscribe_users_to_signal` | `(signal_id: str, user_ids: [int]) → ChannelSubscriptionResponse` | Unsubscribe users. |
| `list_subscribers` | `(signal_id: str, skip=0, limit=50)` | List subscribers of a signal. |
| `list_all_subscribers` | `(signal_id: str, chunk_size=50, max_number=None) → AsyncGenerator` | Auto-paginating subscriber list. |

#### Example — Full signal lifecycle

```python
from symphony.bdk.gen.agent_model.base_signal import BaseSignal

signal_svc = bdk.signals()

# Create
signal = await signal_svc.create_signal(
    BaseSignal(name="Testing signal", query="HASHTAG:hashtag",
               visible_on_profile=False, company_wide=False)
)

# Read
print(await signal_svc.get_signal(signal.id))

# Subscribe / Unsubscribe
await signal_svc.subscribe_users_to_signal(signal.id, True, [13056700580913])
await signal_svc.unsubscribe_users_to_signal(signal.id, [13056700580913])

# List all signals
async for s in await signal_svc.list_all_signals():
    print(s)

# List subscribers
async for sub in await signal_svc.list_all_subscribers(signal.id):
    print(sub)

# Delete
await signal_svc.delete_signal(signal.id)
```

---

## PresenceService — `bdk.presence()`

Source: `symphony/bdk/core/service/presence/presence_service.py` (200 lines)

### Basic Presence

| Method | Signature | Description |
|---|---|---|
| `get_presence` | `() → V2PresenceStatus` | Get the bot's own presence. |
| `get_user_presence` | `(user_id: int, local: bool) → V2UserPresence` | Get another user's presence. `local=True` for pod-local only. |
| `get_all_presence` | `(last_user_id: int, limit: int) → List[V2Presence]` | Get presence for all users in pod (max 5000). |
| `set_presence` | `(status: PresenceStatus, soft: bool) → V2PresenceStatus` | Set bot's presence. `soft=True` = only set if currently `OFFLINE`. |
| `set_user_presence` | `(user_id: int, status: PresenceStatus, soft: bool) → V2PresenceStatus` | Admin: set another user's presence. |
| `external_presence_interest` | `(user_ids: List[int])` | Register interest in external users' presence. |

#### PresenceStatus enum

```python
from symphony.bdk.core.service.presence.presence_service import PresenceStatus
# Values: AVAILABLE, BUSY, AWAY, ON_THE_PHONE, BE_RIGHT_BACK, IN_A_MEETING, OUT_OF_OFFICE, OFF_WORK
```

### Presence Feeds

| Method | Signature | Description |
|---|---|---|
| `create_presence_feed` | `() → str` | Create a feed capturing presence changes. Returns feed ID. |
| `read_presence_feed` | `(feed_id: str) → List[V2Presence]` | Read presence changes since last read. |
| `delete_presence_feed` | `(feed_id: str) → str` | Delete a presence feed. |

---

## SessionService — `bdk.sessions()`

Source: `symphony/bdk/core/service/session/session_service.py` (31 lines)

| Method | Signature | Description |
|---|---|---|
| `get_session` | `() → UserV2` | Get the bot's session info (user ID, display name, email, etc.). |

#### Example

```python
session = await bdk.sessions().get_session()
print(f"Bot: {session.display_name} (ID: {session.id})")
```

---

## HealthService — `bdk.health()`

Source: `symphony/bdk/core/service/health/health_service.py` (47 lines)

| Method | Signature | Description |
|---|---|---|
| `health_check` | `() → V3Health` | Quick health check — returns `UP` if agent is healthy. Requires Agent 2.57.0+. |
| `health_check_extended` | `() → V3Health` | Extended check with per-service status and user connectivity. Requires Agent 2.57.0+. |
| `get_agent_info` | `() → AgentInfo` | Get agent server info (version, hostname). Requires Agent 2.53.0+. |

---

## ApplicationService — `bdk.applications()`

Source: `symphony/bdk/core/service/application/application_service.py` (223 lines)

### Application CRUD

| Method | Signature | Description |
|---|---|---|
| `create_application` | `(application_detail: ApplicationDetail) → ApplicationDetail` | Register a new application. |
| `update_application` | `(app_id: str, application_detail: ApplicationDetail) → ApplicationDetail` | Update an existing application. |
| `delete_application` | `(app_id: str)` | Delete an application. |
| `get_application` | `(app_id: str) → ApplicationDetail` | Get application details. |

### Entitlements

| Method | Signature | Description |
|---|---|---|
| `list_application_entitlements` | `() → List[PodAppEntitlement]` | List app entitlements for the company. |
| `update_application_entitlements` | `(entitlements: [PodAppEntitlement]) → List` | Update company-level app entitlements. |
| `list_user_applications` | `(user_id: int) → List[UserAppEntitlement]` | List app entitlements for a specific user. |
| `update_user_applications` | `(user_id: int, user_app_entitlements: [UserAppEntitlement]) → List` | Replace user's app entitlements. |
| `patch_user_applications` | `(user_id: int, user_app_entitlements: [UserAppEntitlementPatch]) → List` | Partial update of user's app entitlements. |

---

## OBO (On Behalf Of) Services

Access via `bdk.obo_services(obo_session)`:

```python
obo_session = bdk.obo(username="username")
async with bdk.obo_services(obo_session) as obo:
    await obo.messages().send_message(stream_id, "Hello from OBO")
    await obo.messages().suppress_message("URL-Safe-MessageID")
    obo_msg = await obo.messages().send_message(stream_id, "OBO msg")
    await obo.messages().update_message(stream_id, obo_msg.message_id, "Updated")
```

OBO-enabled services: `messages()`, `streams()`, `users()`, `connections()`, `signals()`, `presence()`, `sessions()`.

---

## Pagination Helper

Source: `symphony/bdk/core/service/pagination.py` (93 lines)

The `offset_based_pagination` and `cursor_based_pagination` utilities power all `list_all_*` / `search_all_*` methods. Use them when building custom paginated endpoints:

```python
from symphony.bdk.core.service.pagination import offset_based_pagination

async for item in offset_based_pagination(one_page_func, chunk_size=50, max_number=200):
    process(item)
```
