"""Audio utilities for recording microphone input and playing synthesized speech."""

from __future__ import annotations

import io
import math
import queue
import tempfile
from dataclasses import dataclass

import numpy as np

try:  # pragma: no cover - optional dependency for runtime execution
    import sounddevice as sd
except Exception:  # pragma: no cover
    sd = None  # type: ignore

try:  # pragma: no cover - optional dependency for runtime execution
    import simpleaudio  # noqa: WPS433 (third-party import only when available)
except Exception:  # pragma: no cover
    simpleaudio = None  # type: ignore

import wave

from .config import Settings


class MicrophoneUnavailableError(RuntimeError):
    """Raised when :mod:`sounddevice` is not available."""


class AudioPlaybackError(RuntimeError):
    """Raised when :mod:`simpleaudio` is not installed or playback fails."""


@dataclass(slots=True)
class RecordingResult:
    """Container for recorded audio."""

    audio: bytes
    duration: float


class VoiceRecorder:
    """Capture audio from the system microphone with basic VAD controls."""

    def __init__(self, settings: Settings) -> None:
        if sd is None:  # pragma: no cover - dependent on optional runtime dependency
            raise MicrophoneUnavailableError(
                "sounddevice is required for recording audio. Install optional dependencies "
                "or run the project on a machine with microphone support."
            )

        self.settings = settings
        self._queue: queue.Queue[np.ndarray] = queue.Queue()
        self._block_size = int(settings.sample_rate * settings.block_duration)
        self._silence_samples = int(settings.max_silence_seconds / settings.block_duration)

    def record(self) -> RecordingResult | None:
        """Record a single utterance from the microphone.

        The recorder collects audio chunks until it detects a sufficient amount of
        silence or the configured maximum duration is reached. The raw audio is
        returned as a WAV byte sequence alongside the captured duration.
        """

        frames: list[np.ndarray] = []
        silence_streak = 0
        captured_blocks = 0

        def _callback(indata: np.ndarray, frames: int, time, status) -> None:  # pragma: no cover - callback invoked by sounddevice
            if status:
                # Drop frames with errors to keep the buffer in sync.
                return
            self._queue.put_nowait(indata.copy())

        with sd.InputStream(
            samplerate=self.settings.sample_rate,
            channels=self.settings.channels,
            dtype=self.settings.dtype,
            blocksize=self._block_size,
            callback=_callback,
        ):
            max_blocks = math.ceil(
                self.settings.max_recording_seconds / self.settings.block_duration
            )
            min_blocks = max(
                1, math.ceil(self.settings.min_recording_seconds / self.settings.block_duration)
            )

            while captured_blocks < max_blocks:
                try:
                    chunk = self._queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                frames.append(chunk)
                captured_blocks += 1

                rms = float(np.sqrt(np.mean(np.square(chunk))))
                if rms < self.settings.silence_threshold:
                    silence_streak += 1
                else:
                    silence_streak = 0

                if captured_blocks >= min_blocks and silence_streak >= self._silence_samples:
                    break

        if not frames:
            return None

        audio = np.concatenate(frames, axis=0)
        duration = len(audio) / float(self.settings.sample_rate)

        # Convert to int16 PCM for compatibility with OpenAI endpoints.
        audio = np.clip(audio, -1.0, 1.0)
        pcm_data = (audio * np.iinfo(np.int16).max).astype(np.int16)

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(self.settings.channels)
            wav_file.setsampwidth(2)  # 16-bit PCM
            wav_file.setframerate(self.settings.sample_rate)
            wav_file.writeframes(pcm_data.tobytes())

        return RecordingResult(audio=buffer.getvalue(), duration=duration)


class AudioPlayer:
    """Simple WAV playback helper using :mod:`simpleaudio`."""

    def __init__(self) -> None:
        if simpleaudio is None:  # pragma: no cover - optional runtime dependency
            self._enabled = False
        else:
            self._enabled = True

    @property
    def available(self) -> bool:
        """Return ``True`` when playback dependencies are installed."""

        return self._enabled

    def play(self, wav_audio: bytes) -> None:
        """Play a short WAV clip from memory."""

        if not self._enabled:
            raise AudioPlaybackError(
                "simpleaudio is required for playback. Install optional dependencies to "
                "hear Alloy's responses or disable audio playback."
            )

        with wave.open(io.BytesIO(wav_audio), "rb") as wav_file:
            audio_data = wav_file.readframes(wav_file.getnframes())
            wave_object = simpleaudio.WaveObject(
                audio_data,
                num_channels=wav_file.getnchannels(),
                bytes_per_sample=wav_file.getsampwidth(),
                sample_rate=wav_file.getframerate(),
            )

        play_obj = wave_object.play()
        play_obj.wait_done()


def save_wav_to_temp_file(data: bytes, suffix: str = ".wav") -> str:
    """Persist audio bytes to a temporary file and return the path."""

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        return tmp.name


__all__ = [
    "AudioPlayer",
    "AudioPlaybackError",
    "MicrophoneUnavailableError",
    "RecordingResult",
    "VoiceRecorder",
    "save_wav_to_temp_file",
]
