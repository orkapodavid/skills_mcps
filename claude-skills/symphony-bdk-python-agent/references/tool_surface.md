# Suggested MCP / Tool Surface (BDK-backed)

Practical tool set for an MCP server (or any "LLM tool calling" wrapper) built on `symphony-bdk-python`. Each tool maps to one or more BDK service methods.

## Messaging

### Tool: send_message
- **Inputs**: `stream_id` (string), `message_ml` (string)
- **BDK**: `bdk.messages().send_message(stream_id, Message(content=message_ml))`

### Tool: send_message_with_attachments
- **Inputs**: `stream_id`, `message_ml`, `files` (list of file paths)
- **BDK**: `Message(content=message_ml, attachments=[open(f, "rb") for f in files])`

### Tool: search_messages
- **Inputs**: `query` (string), `stream_id` (optional), `from_date` / `to_date` (optional)
- **BDK**: `bdk.messages().search_messages(query, ...)`

### Tool: get_message
- **Inputs**: `message_id` (string)
- **BDK**: `bdk.messages().get_message(message_id)`

### Tool: suppress_message
- **Inputs**: `message_id` (string)
- **BDK**: `bdk.messages().suppress_message(message_id)`

## Streams (Rooms / IMs)

### Tool: get_stream
- **Inputs**: `stream_id` (string)
- **BDK**: `bdk.streams().get_stream(stream_id)`

### Tool: create_im
- **Inputs**: `user_ids` (list of integers)
- **BDK**: `bdk.streams().create_im(user_ids)`

### Tool: create_room
- **Inputs**: `name`, `description`, `public` (bool), `read_only` (bool)
- **BDK**: `bdk.streams().create_room(room_attrs)`

### Tool: list_room_members
- **Inputs**: `stream_id` (string)
- **BDK**: `bdk.streams().list_room_members(stream_id)`

### Tool: add_user_to_room
- **Inputs**: `user_id` (int), `stream_id` (string)
- **BDK**: `bdk.streams().add_member_to_room(user_id, stream_id)`

### Tool: remove_user_from_room
- **Inputs**: `user_id` (int), `stream_id` (string)
- **BDK**: `bdk.streams().remove_member_from_room(user_id, stream_id)`

### Tool: search_rooms
- **Inputs**: `query` (string)
- **BDK**: `bdk.streams().search_rooms(query)`

## Users

### Tool: search_users
- **Inputs**: `query` (string), `local` (bool, default True)
- **BDK**: `bdk.users().search_users(query, local)`

### Tool: get_user
- **Inputs**: `user_id` (int)
- **BDK**: `bdk.users().list_users_by_ids([user_id])`

## Connections

### Tool: send_connection_request
- **Inputs**: `user_id` (int)
- **BDK**: `bdk.connections().create_connection(user_id)`

### Tool: accept_connection
- **Inputs**: `user_id` (int)
- **BDK**: `bdk.connections().accept_connection(user_id)`

### Tool: list_connections
- **Inputs**: `status` (string, optional: "all"/"pending_incoming"/"pending_outgoing"/"accepted"/"rejected")
- **BDK**: `bdk.connections().list_connections(status)`

## Signals

### Tool: create_signal
- **Inputs**: `name` (string), `query` (string)
- **BDK**: `bdk.signals().create_signal(signal)`

### Tool: list_signals
- **Inputs**: `skip` (int), `limit` (int)
- **BDK**: `bdk.signals().list_signals(skip, limit)`

## Presence

### Tool: get_presence
- **Inputs**: none (bot's own) or `user_id` (int)
- **BDK**: `bdk.presence().get_presence()` or `bdk.presence().get_user_presence(user_id)`

### Tool: set_presence
- **Inputs**: `status` (string: AVAILABLE, BUSY, DO_NOT_DISTURB, AWAY, etc.)
- **BDK**: `bdk.presence().set_presence(status)`

## Operational

### Tool: healthcheck
- **Inputs**: none
- **BDK**: `bdk.health().health_check()` or `bdk.health().health_check_extended()`

### Tool: get_session
- **Inputs**: none
- **BDK**: `bdk.sessions().get_session()` — returns bot user ID, display name, etc.

## Design Principles for Safe Tools

- Treat `stream_id`, `user_id`, and room identifiers as *untrusted inputs* — validate format.
- Never return session tokens, key manager tokens, or private key material.
- Add allow-lists for rooms the bot may post into (enterprise controls).
- Rate-limit write operations (send, create, suppress) to prevent abuse.
- Log tool invocations (caller, inputs, timestamp) for audit trails.
- Consider read-only vs. write tool tiers with separate authorization.
