# Alloy Voice Assistant (Inspired)

This repository implements a lightweight, microphone-driven voice assistant inspired by [svpino/alloy-voice-assistant](https://github.com/svpino/alloy-voice-assistant). It demonstrates how to combine OpenAI's transcription, reasoning, and text-to-speech capabilities to hold natural conversations using the "Alloy" voice.

## Features

- 🎙️ **Hands-free conversations** – capture speech from your default microphone with automatic silence detection.
- 🤖 **Conversational context** – maintain a rolling dialogue history so Alloy can give relevant follow-up answers.
- 🗣️ **Voice responses** – request synthesized speech from OpenAI's text-to-speech models and play it back locally.
- ⚙️ **Configurable runtime** – override models, sampling parameters, and prompts via environment variables.
- ✅ **Tested utilities** – includes unit tests for configuration parsing, conversation memory, and message assembly.

## Requirements

- Python 3.10+
- An OpenAI API key with access to GPT-4o models
- A working microphone (for recording) and speakers/headphones (for playback)

Install the runtime dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

> **Note:** Audio capture requires `sounddevice` (PortAudio). On Linux you may need to install system packages such as `libportaudio2` before installing Python dependencies.

## Configuration

Set the required API key and optional overrides in your shell before launching the assistant:

| Variable | Description | Default |
| --- | --- | --- |
| `OPENAI_API_KEY` | **Required.** Your OpenAI API key. | — |
| `ALLOY_MODEL` | Model used for reasoning responses. | `gpt-4o-mini` |
| `ALLOY_TRANSCRIPTION_MODEL` | Model used for speech-to-text. | `gpt-4o-mini-transcribe` |
| `ALLOY_TTS_MODEL` | Model used for text-to-speech. | `gpt-4o-mini-tts` |
| `ALLOY_VOICE` | Voice name for synthesized audio. | `alloy` |
| `ALLOY_SAMPLE_RATE` | Microphone sample rate. | `16000` |
| `ALLOY_BLOCK_DURATION` | Length (seconds) of audio chunks captured per buffer. | `0.5` |
| `ALLOY_SILENCE_THRESHOLD` | RMS threshold below which audio counts as silence. | `0.015` |
| `ALLOY_MAX_SILENCE` | How long (seconds) of silence ends a recording. | `1.5` |
| `ALLOY_MAX_RECORDING` | Hard limit (seconds) for a single utterance. | `30.0` |
| `ALLOY_MIN_RECORDING` | Minimum duration (seconds) before silence ends the capture. | `0.4` |
| `ALLOY_CONVERSATION_WINDOW` | Number of recent messages to retain in memory. | `8` |
| `ALLOY_SYSTEM_PROMPT` | System prompt used to steer Alloy's personality. | Helpful Alloy prompt |

## Usage

Activate your environment and run the module:

```bash
python -m alloy_assistant
```

- Press **Enter** to begin recording. Speak naturally and pause; the recorder automatically stops after a short silence.
- Alloy prints the transcript, generates a response, and (if `simpleaudio` is installed) plays synthesized speech back.
- Type `quit`, `q`, or `exit` to leave the session.

To hide the ASCII art banner:

```bash
python -m alloy_assistant --no-banner
```

## Running tests

Run the bundled unit tests with Python's built-in unittest discovery:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## Project structure

```
├── pyproject.toml          # Packaging metadata and dependencies
├── src/alloy_assistant     # Application source code
│   ├── assistant.py        # CLI entry point and runtime loop
│   ├── audio.py            # Microphone recorder and audio playback helpers
│   ├── client.py           # OpenAI client wrapper + message builder
│   ├── config.py           # Environment-driven configuration values
│   ├── conversation.py     # Rolling conversation memory utilities
│   └── __main__.py         # Enables `python -m alloy_assistant`
└── tests                   # Unit tests for core helpers
```

## Troubleshooting

- **No microphone detected:** ensure `sounddevice` is installed and your OS exposes a default input device. Running `python -m sounddevice` can help diagnose driver issues.
- **No audio playback:** install `simpleaudio` or disable playback (responses will still be printed).
- **API errors:** verify your OpenAI quota and that the configured models are available to your API key.

Have fun building on top of this foundation! Feel free to adapt the assistant's prompt, expand the UI, or integrate home-automation commands just like the original Alloy project.
