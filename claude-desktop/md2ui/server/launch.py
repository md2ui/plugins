"""Start md2ui's window MCP server from the published package (md2ui ADR-605).

Claude Desktop runs this file with its own ``python3``, so it uses the standard
library only, and it never writes to stdout: once the server starts, stdout is
the MCP protocol (ADR-602). A GUI app does not inherit the shell's PATH, so it
finds ``uvx`` itself, then replaces itself with the command the md2ui README
registers by hand:

    uvx --from md2ui==0.1.0a1 md2ui-mcp-demo --fetch [--theme <THEME.md>]

It runs on the user's machine, so its previews load pictures, and the fonts md2ui
locks, as its window does (``--fetch``).

Run it: ``[MD2UI_THEME=<THEME.md>] python3 launch.py [--dry-run]``; ``--dry-run``
prints the command instead of running it.
"""

from __future__ import annotations

import os
import shlex
import shutil
import sys
from pathlib import Path

# The md2ui release this extension runs.
PACKAGE = "md2ui==0.1.0a1"
# Where uv's installers put it, for when PATH is a GUI app's bare default.
UVX_FALLBACKS = (
    "~/.local/bin/uvx",
    "~/.cargo/bin/uvx",
    "/opt/homebrew/bin/uvx",
    "/usr/local/bin/uvx",
)


def _say(message: str) -> None:
    print(f"md2ui: {message}", file=sys.stderr)


def find_uvx() -> str | None:
    found = shutil.which("uvx")
    if found:
        return found
    for candidate in UVX_FALLBACKS:
        path = Path(candidate).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
    return None


def main(argv: list[str]) -> int:
    theme = os.environ.get("MD2UI_THEME", "").strip()
    if theme.startswith("${"):
        theme = ""  # an unset optional setting may arrive unsubstituted
    if theme:
        theme_path = Path(theme).expanduser()
        if not theme_path.is_file():
            _say(f"no such theme: {theme_path}")
            return 2
        theme = str(theme_path)

    uvx = find_uvx()
    if uvx is None:
        _say("uvx not found on PATH or in " + ", ".join(UVX_FALLBACKS) + "; install uv")
        return 2
    command = [uvx, "--from", PACKAGE, "md2ui-mcp-demo", "--fetch"]
    command += ["--theme", theme] if theme else []
    if "--dry-run" in argv:
        print(shlex.join(command))
        return 0
    os.execv(uvx, command)  # replaces this process: nothing after it runs


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
