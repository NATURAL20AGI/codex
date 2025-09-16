"""Unit tests for the conversation memory helper."""

from __future__ import annotations

import unittest

from alloy_assistant.conversation import ConversationMemory


class ConversationMemoryTests(unittest.TestCase):
    def test_preserves_latest_messages(self) -> None:
        memory = ConversationMemory(max_messages=3)

        memory.add("user", "hello")
        memory.add("assistant", "hi there")
        memory.add("user", "what's the weather?")
        memory.add("assistant", "It's sunny!")

        history = list(memory.as_pairs())
        self.assertEqual(
            history,
            [
                ("assistant", "hi there"),
                ("user", "what's the weather?"),
                ("assistant", "It's sunny!"),
            ],
        )

    def test_ignores_empty_messages(self) -> None:
        memory = ConversationMemory(max_messages=2)

        memory.add("user", "   ")
        memory.add("assistant", "Sure!")

        self.assertEqual(list(memory.as_pairs()), [("assistant", "Sure!")])

    def test_requires_positive_window(self) -> None:
        with self.assertRaises(ValueError):
            ConversationMemory(max_messages=0)


if __name__ == "__main__":  # pragma: no cover - unittest runner
    unittest.main()
