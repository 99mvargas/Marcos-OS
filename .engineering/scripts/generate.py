#!/usr/bin/env python3
"""Regenerate the full engineering-state pipeline in one command.

Repository -> facts.json -> (+ decisions.json) -> context.json -> current.md

Run: python .engineering/scripts/generate.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate_facts   # noqa: E402
import generate_context  # noqa: E402
import generate_current_md  # noqa: E402


def main() -> None:
    generate_facts.main()
    print("wrote .engineering/facts.json")
    generate_context.main()
    print("wrote .engineering/context.json")
    generate_current_md.main()
    print("wrote .context/current.md")


if __name__ == "__main__":
    main()
