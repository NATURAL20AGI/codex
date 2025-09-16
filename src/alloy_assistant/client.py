"""OpenAI API client wrappers used by the voice assistant."""

from __future__ import annotations

import base64
import io
import os
import tempfile
from dataclasses import dataclass
from typing import Iterable, Sequence

try:  # pragma: no cover - optional dependency for runtime execution
    from openai import OpenAI
    from openai.types.chat import ChatCompletionMessageParam
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore
    ChatCompletionMessageParam = dict  # type: ignore

from .config import Settings


@dataclass(slots=True)
class ChatResult:
    """Container for assistant responses."""

    text: str
    audio: bytes | None = None


class OpenAIClient:
    """Small convenience wrapper around the official OpenAI Python SDK."""

    def __init__(self, settings: Settings) -> None:
        if OpenAI is None:  # pragma: no cover - optional runtime dependency
            raise RuntimeError(
                "The `openai` package is required to run the assistant. Install the project "
                "dependencies (pip install -e .) before launching the app."
            )

        self.settings = settings
        self._client = OpenAI(api_key=settings.openai_api_key)

    def transcribe(self, wav_audio: bytes) -> str:
        """Send audio to OpenAI and return the transcription text."""

        audio_buffer = io.BytesIO(wav_audio)
        audio_buffer.name = "speech.wav"  # type: ignore[attr-defined]

        transcription = self._client.audio.transcriptions.create(  # type: ignore[no-untyped-call]
            model=self.settings.transcription_model,
            file=audio_buffer,
        )
        text = getattr(transcription, "text", "")
        return text.strip()

    def complete(self, messages: Sequence[ChatCompletionMessageParam]) -> ChatResult:
        """Request a textual response and optional synthesized audio."""

        response = self._client.responses.create(  # type: ignore[no-untyped-call]
            model=self.settings.model,
            input=list(messages),
            audio={"voice": self.settings.voice, "format": "wav"},
        )

        text_fragments: list[str] = []
        audio_bytes: bytes | None = None

        for item in getattr(response, "output", []):
            contents = getattr(item, "content", [])
            for content in contents:
                content_type = getattr(content, "type", None)
                if content_type == "output_text":
                    text_fragments.append(getattr(content, "text", ""))
                elif content_type == "output_audio" and audio_bytes is None:
                    audio = getattr(content, "audio", None)
                    if audio is None:
                        continue
                    data = getattr(audio, "data", None)
                    if isinstance(data, str):
                        try:
                            audio_bytes = base64.b64decode(data)
                        except Exception:  # pragma: no cover - defensive branch
                            audio_bytes = None

        text = "".join(text_fragments).strip()
        if audio_bytes is None and text:
            audio_bytes = self._synthesize_text(text)

        return ChatResult(text=text, audio=audio_bytes)

    def _synthesize_text(self, text: str) -> bytes | None:
        """Fallback TTS helper used when the responses API does not return audio."""

        if not text:
            return None

        try:
            with self._client.audio.speech.with_streaming_response.create(  # type: ignore[no-untyped-call]
                model=self.settings.tts_model,
                voice=self.settings.voice,
                input=text,
                format="wav",
            ) as response:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    response.stream_to_file(tmp.name)
                    tmp.seek(0)
                    data = tmp.read()
            os.unlink(tmp.name)
            return data
        except AttributeError:  # pragma: no cover - fallback for older SDK versions
            speech = self._client.audio.speech.create(  # type: ignore[no-untyped-call]
                model=self.settings.tts_model,
                voice=self.settings.voice,
                input=text,
                format="wav",
            )
            audio = getattr(speech, "audio", None)
            if isinstance(audio, bytes):
                return audio
            data = getattr(speech, "data", None)
            if isinstance(data, str):
                try:
                    return base64.b64decode(data)
                except Exception:  # pragma: no cover - defensive branch
                    return None
            if hasattr(speech, "read"):
                return speech.read()
            return None


def build_messages(settings: Settings, history: Iterable[tuple[str, str]], user_text: str) -> list[ChatCompletionMessageParam]:
    """Assemble messages for the Responses API."""

    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": settings.system_prompt,
                }
            ],
        }
    ]

    for role, content in history:
        messages.append(
            {
                "role": role,
                "content": [
                    {
                        "type": "text",
                        "text": content,
                    }
                ],
            }
        )

    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_text,
                }
            ],
        }
    )

    return messages


__all__ = ["ChatResult", "OpenAIClient", "build_messages"]
