"""Unit tests for configuration helpers using :mod:`unittest`."""

from __future__ import annotations

import os
import unittest
from unittest import mock

from alloy_assistant.config import (
    DEFAULT_MODEL,
    DEFAULT_SYSTEM_PROMPT,
    Settings,
)


class SettingsTests(unittest.TestCase):
    """Verify environment parsing logic."""

    def test_defaults(self) -> None:
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            settings = Settings.from_env()

        self.assertEqual(settings.openai_api_key, "test-key")
        self.assertEqual(settings.model, DEFAULT_MODEL)
        self.assertEqual(settings.system_prompt, DEFAULT_SYSTEM_PROMPT)
        self.assertEqual(settings.sample_rate, 16_000)

    def test_overrides(self) -> None:
        env = {
            "OPENAI_API_KEY": "override-key",
            "ALLOY_MODEL": "test-model",
            "ALLOY_SAMPLE_RATE": "22050",
            "ALLOY_BLOCK_DURATION": "0.1",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            settings = Settings.from_env()

        self.assertEqual(settings.openai_api_key, "override-key")
        self.assertEqual(settings.model, "test-model")
        self.assertEqual(settings.sample_rate, 22050)
        self.assertAlmostEqual(settings.block_duration, 0.1)

    def test_missing_api_key(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                Settings.from_env()


if __name__ == "__main__":  # pragma: no cover - unittest runner
    unittest.main()
