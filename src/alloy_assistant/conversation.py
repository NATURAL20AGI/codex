"""Conversation history helpers for the voice assistant."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Iterator

Role = str


@dataclass(slots=True)
class Message:
    """Simple message container."""

    role: Role
    content: str


class ConversationMemory:
    """Maintain a rolling window of the conversation with the assistant."""

    def __init__(self, max_messages: int) -> None:
        if max_messages <= 0:
            raise ValueError("max_messages must be greater than zero")
        self._messages: Deque[Message] = deque(maxlen=max_messages)

    def add(self, role: Role, content: str) -> None:
        """Append a new message to the history."""

        cleaned = content.strip()
        if not cleaned:
            return
        self._messages.append(Message(role=role, content=cleaned))

    def as_pairs(self) -> Iterator[tuple[Role, str]]:
        """Yield history entries as ``(role, content)`` tuples."""

        for message in self._messages:
            yield message.role, message.content

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._messages)

    def __iter__(self) -> Iterator[Message]:  # pragma: no cover - trivial
        return iter(self._messages)


__all__ = ["ConversationMemory", "Message", "Role"]
