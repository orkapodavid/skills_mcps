"""BDK-backed tools layer skeleton.

Goal:
- Provide a reusable wrapper class whose async methods map 1:1 to "tool calls".
- Useful as the implementation layer for an MCP server, REST API, or agent framework.

This file intentionally avoids choosing a specific MCP library/framework.
Adapt the class methods to match your tool surface requirements.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from symphony.bdk.core.service.message.model import Message
from symphony.bdk.core.symphony_bdk import SymphonyBdk


@dataclass
class SendMessageInput:
    stream_id: str
    message_ml: str


@dataclass
class SearchMessagesInput:
    query: str
    stream_id: Optional[str] = None
    limit: int = 25


@dataclass
class StreamInput:
    stream_id: str


@dataclass
class RoomMemberInput:
    user_id: int
    stream_id: str


@dataclass
class UserSearchInput:
    query: str
    local: bool = True


class SymphonyTools:
    """Thin wrapper mapping tool calls to BDK service methods."""

    def __init__(self, bdk: SymphonyBdk):
        self._bdk = bdk
        self._messages = bdk.messages()
        self._streams = bdk.streams()
        self._users = bdk.users()
        self._health = bdk.health()
        self._sessions = bdk.sessions()

    # ── Messaging ──────────────────────────────────────────────

    async def send_message(self, inp: SendMessageInput) -> dict[str, Any]:
        """Send a MessageML message to a stream."""
        result = await self._messages.send_message(
            inp.stream_id, Message(content=inp.message_ml)
        )
        return {"message_id": result.message_id if result else None}

    async def search_messages(self, inp: SearchMessagesInput) -> list[dict]:
        """Search messages by query string."""
        results = await self._messages.search_messages(
            inp.query, stream_id=inp.stream_id, limit=inp.limit
        )
        return [{"message_id": m.message_id, "text": m.message} for m in results]

    # ── Streams ────────────────────────────────────────────────

    async def get_stream(self, inp: StreamInput) -> dict[str, Any]:
        """Get stream information."""
        stream = await self._streams.get_stream(inp.stream_id)
        return {"stream_id": stream.id, "stream_type": stream.stream_type.type}

    async def list_room_members(self, inp: StreamInput) -> list[dict]:
        """List members of a room."""
        members = await self._streams.list_room_members(inp.stream_id)
        return [{"user_id": m.id, "owner": m.owner} for m in members]

    async def add_user_to_room(self, inp: RoomMemberInput) -> None:
        """Add a user to a room."""
        await self._streams.add_member_to_room(inp.user_id, inp.stream_id)

    async def remove_user_from_room(self, inp: RoomMemberInput) -> None:
        """Remove a user from a room."""
        await self._streams.remove_member_from_room(inp.user_id, inp.stream_id)

    # ── Users ──────────────────────────────────────────────────

    async def search_users(self, inp: UserSearchInput) -> list[dict]:
        """Search for users by query."""
        results = await self._users.search_users(inp.query, local=inp.local)
        return [
            {"user_id": u.id, "display_name": u.display_name, "email": u.email_address}
            for u in results
        ]

    # ── Operational ────────────────────────────────────────────

    async def healthcheck(self) -> dict[str, Any]:
        """Run a health check against the BDK services."""
        health = await self._health.health_check_extended()
        return {"status": health.status, "services": health.services}

    async def get_session(self) -> dict[str, Any]:
        """Get the bot's session info (user ID, display name)."""
        session = await self._sessions.get_session()
        return {"user_id": session.id, "display_name": session.display_name}
