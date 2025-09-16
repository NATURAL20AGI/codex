"""Configuration helpers for the alloy-inspired voice assistant."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TRANSCRIPTION_MODEL = "gpt-4o-mini-transcribe"
DEFAULT_TTS_MODEL = "gpt-4o-mini-tts"
DEFAULT_VOICE = "alloy"
DEFAULT_SYSTEM_PROMPT = (
    "You are Alloy, a helpful, proactive voice assistant that keeps responses concise "
    "and conversational. Provide practical answers and optional follow up suggestions."
)
DEFAULT_SAMPLE_RATE = 16_000
DEFAULT_CHANNELS = 1
DEFAULT_DTYPE = "float32"
DEFAULT_BLOCK_DURATION = 0.5
DEFAULT_SILENCE_THRESHOLD = 0.015
DEFAULT_MAX_SILENCE_SECONDS = 1.5
DEFAULT_MAX_RECORDING_SECONDS = 30.0
DEFAULT_MIN_RECORDING_SECONDS = 0.4
DEFAULT_CONVERSATION_WINDOW = 8


@dataclass(slots=True)
class Settings:
    """Application settings loaded from the environment."""

    openai_api_key: str
    model: str = DEFAULT_MODEL
    transcription_model: str = DEFAULT_TRANSCRIPTION_MODEL
    tts_model: str = DEFAULT_TTS_MODEL
    voice: str = DEFAULT_VOICE
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    sample_rate: int = DEFAULT_SAMPLE_RATE
    channels: int = DEFAULT_CHANNELS
    dtype: str = DEFAULT_DTYPE
    block_duration: float = DEFAULT_BLOCK_DURATION
    silence_threshold: float = DEFAULT_SILENCE_THRESHOLD
    max_silence_seconds: float = DEFAULT_MAX_SILENCE_SECONDS
    max_recording_seconds: float = DEFAULT_MAX_RECORDING_SECONDS
    min_recording_seconds: float = DEFAULT_MIN_RECORDING_SECONDS
    conversation_window: int = DEFAULT_CONVERSATION_WINDOW

    @classmethod
    def from_env(cls, env: Optional[dict[str, str]] = None) -> "Settings":
        """Create settings from the process environment.

        Parameters
        ----------
        env:
            Optional mapping used instead of :data:`os.environ` for testing.

        Returns
        -------
        Settings
            Populated configuration dataclass.

        Raises
        ------
        RuntimeError
            If the OpenAI API key is missing.
        """

        env_map = dict(os.environ if env is None else env)

        api_key = env_map.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required to run the voice assistant."
            )

        def _float(name: str, default: float) -> float:
            value = env_map.get(name)
            if value is None:
                return default
            try:
                return float(value)
            except ValueError:
                return default

        def _int(name: str, default: int) -> int:
            value = env_map.get(name)
            if value is None:
                return default
            try:
                return int(value)
            except ValueError:
                return default

        return cls(
            openai_api_key=api_key,
            model=env_map.get("ALLOY_MODEL", DEFAULT_MODEL),
            transcription_model=env_map.get(
                "ALLOY_TRANSCRIPTION_MODEL", DEFAULT_TRANSCRIPTION_MODEL
            ),
            tts_model=env_map.get("ALLOY_TTS_MODEL", DEFAULT_TTS_MODEL),
            voice=env_map.get("ALLOY_VOICE", DEFAULT_VOICE),
            system_prompt=env_map.get("ALLOY_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT),
            sample_rate=_int("ALLOY_SAMPLE_RATE", DEFAULT_SAMPLE_RATE),
            channels=_int("ALLOY_CHANNELS", DEFAULT_CHANNELS),
            dtype=env_map.get("ALLOY_DTYPE", DEFAULT_DTYPE),
            block_duration=_float("ALLOY_BLOCK_DURATION", DEFAULT_BLOCK_DURATION),
            silence_threshold=_float(
                "ALLOY_SILENCE_THRESHOLD", DEFAULT_SILENCE_THRESHOLD
            ),
            max_silence_seconds=_float(
                "ALLOY_MAX_SILENCE", DEFAULT_MAX_SILENCE_SECONDS
            ),
            max_recording_seconds=_float(
                "ALLOY_MAX_RECORDING", DEFAULT_MAX_RECORDING_SECONDS
            ),
            min_recording_seconds=_float(
                "ALLOY_MIN_RECORDING", DEFAULT_MIN_RECORDING_SECONDS
            ),
            conversation_window=_int(
                "ALLOY_CONVERSATION_WINDOW", DEFAULT_CONVERSATION_WINDOW
            ),
        )


__all__ = [
    "Settings",
    "DEFAULT_MODEL",
    "DEFAULT_TRANSCRIPTION_MODEL",
    "DEFAULT_TTS_MODEL",
    "DEFAULT_VOICE",
    "DEFAULT_SYSTEM_PROMPT",
]
