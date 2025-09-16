"""Allow running ``python -m alloy_assistant`` to launch the assistant."""

from .assistant import main

if __name__ == "__main__":  # pragma: no cover - manual execution only
    raise SystemExit(main())
