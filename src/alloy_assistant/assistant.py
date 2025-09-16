"""Interactive CLI entry point for the alloy-inspired voice assistant."""

from __future__ import annotations

import argparse
import sys
import textwrap
import time
from contextlib import contextmanager
from typing import Callable, Iterator

from .audio import (
    AudioPlaybackError,
    AudioPlayer,
    MicrophoneUnavailableError,
    VoiceRecorder,
)
from .client import OpenAIClient, build_messages
from .config import Settings
from .conversation import ConversationMemory


def _format_header() -> str:
    banner = r"""
     ___    _ _                   __     __           _           _   _              _   _             _
    / _ \__| (_)_ __   ___ _   _  \ \   / /__ _ __ __| | ___ _ __ | |_(_) ___  ___  | | | |_   _  __ _| |_ ___
   / /_\/ _` | | '_ \ / _ \ | | |  \ \ / / _ \ '__/ _` |/ _ \ '_ \| __| |/ _ \/ __| | |_| | | | |/ _` | __/ _ \
  / /_\\ (_| | | | | |  __/ |_| |   \ V /  __/ | | (_| |  __/ | | | |_| |  __/\__ \ |  _  | |_| | (_| | ||  __/
  \____/\__,_|_|_| |_|\___|\__,_|    \_/ \___|_|  \__,_|\___|_| |_|\__|_|\___||___/ |_| |_|\__,_|\__,_|\__\___|
    """
    return textwrap.dedent(banner).strip("\n")


@contextmanager
def _timer() -> Iterator[Callable[[], float]]:  # pragma: no cover - used for CLI reporting
    start = time.perf_counter()
    yield lambda: time.perf_counter() - start


def run(settings: Settings) -> int:
    """Run the interactive assistant loop."""

    try:
        client = OpenAIClient(settings)
    except RuntimeError as exc:  # pragma: no cover - runtime dependency check
        print(f"Unable to start assistant: {exc}", file=sys.stderr)
        return 1

    try:
        recorder = VoiceRecorder(settings)
    except MicrophoneUnavailableError as exc:  # pragma: no cover - runtime dependency check
        print(f"Unable to access microphone: {exc}", file=sys.stderr)
        return 1

    player = AudioPlayer()
    memory = ConversationMemory(max_messages=settings.conversation_window)

    print("Press Enter to speak. Type 'quit' to exit.")

    while True:
        user_input = input("\n▶  ").strip()
        if user_input.lower() in {"quit", "exit", "q"}:
            print("Goodbye! 👋")
            return 0
        if user_input:
            print("Type Enter without text to record audio.")
            continue

        print("Listening... (speak clearly into your microphone)")

        with _timer() as elapsed:
            recording = recorder.record()
        if recording is None:
            print("No audio captured. Try speaking louder or adjusting the microphone.")
            continue

        print(f"Captured {recording.duration:.1f}s of audio in {elapsed():.2f}s. Transcribing...")

        with _timer() as elapsed:
            transcript = client.transcribe(recording.audio)
        if not transcript:
            print("I couldn't understand that. Let's try again.")
            continue

        print(f"You said: {transcript}")
        with _timer() as elapsed:
            messages = build_messages(settings, memory.as_pairs(), transcript)
            response = client.complete(messages)
        if not response.text:
            print("I didn't get a response from the model. Please try again.")
            continue

        print(f"Alloy: {response.text}")
        memory.add("user", transcript)
        memory.add("assistant", response.text)

        if response.audio and player.available:
            try:
                player.play(response.audio)
            except AudioPlaybackError as exc:  # pragma: no cover - optional runtime dependency
                print(f"Audio playback failed: {exc}")

        print(f"⏱️  Response latency: {elapsed():.2f}s")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description="Run the Alloy-inspired voice assistant")
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Hide the ASCII art banner on startup.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Module entry point used by :mod:`python -m alloy_assistant`."""

    args = parse_args(argv)

    try:
        settings = Settings.from_env()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not args.no_banner:
        print(_format_header())
        print()

    return run(settings)


if __name__ == "__main__":  # pragma: no cover - manual execution only
    raise SystemExit(main())
