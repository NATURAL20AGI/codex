"""Alloy-inspired voice assistant package."""

from __future__ import annotations

from typing import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    """Lazy entry point that defers heavy imports until execution time."""

    from .assistant import main as _main

    return _main(list(argv) if argv is not None else None)


__all__ = ["main"]
