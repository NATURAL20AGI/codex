"""Unit tests for the message builder helper."""

from __future__ import annotations

import os
import unittest
from unittest import mock

from alloy_assistant.client import build_messages
from alloy_assistant.config import Settings


class BuildMessagesTests(unittest.TestCase):
    def test_includes_history_and_new_prompt(self) -> None:
        env = {"OPENAI_API_KEY": "test"}
        with mock.patch.dict(os.environ, env, clear=True):
            settings = Settings.from_env()

        history = [("user", "hello"), ("assistant", "hi")]
        messages = build_messages(settings, history, "How are you?")

        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[1]["content"][0]["text"], "hello")
        self.assertEqual(messages[2]["role"], "assistant")
        self.assertEqual(messages[-1]["role"], "user")
        self.assertEqual(messages[-1]["content"][0]["text"], "How are you?")


if __name__ == "__main__":  # pragma: no cover - unittest runner
    unittest.main()
