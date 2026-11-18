"""Tests for the OpenAI plugin that launches md2ui's native window, for
ChatGPT Desktop and Codex, from the published md2ui package.

The live test starts the server exactly as the host would, from a folder of its
own, so it needs uv and the network the first time. Run with the md2ui release
the plugin names installed:

    uv run --python 3.13 --with md2ui==0.1.0a1 python tests/codex_packaging_tests.py
"""

import asyncio
import json
import tempfile
from importlib import metadata
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "codex/plugins/md2ui"
# The release installed here, which the plugin must name.
PIN = f"md2ui=={metadata.version('md2ui')}"


def _json(path: Path) -> dict:
    return json.loads(path.read_text())


def _server() -> dict:
    return _json(PACKAGE / ".mcp.json")["mcpServers"]["md2ui"]


def test_manifest_names_one_local_stdio_server():
    compatibility = _json(PACKAGE / ".codex-plugin/plugin.json")
    assert not (PACKAGE / "plugin.json").exists()
    assert not (PACKAGE / "mcp.json").exists()
    assert compatibility["name"] == "md2ui"
    assert compatibility["requires_local_executor"] is True
    assert compatibility["skills"] == "./skills/"
    assert compatibility["interface"]["displayName"] == "md2ui"
    assert compatibility["mcpServers"] == "./.mcp.json"

    server = _server()
    assert set(server) == {"command", "enabled", "args"}, server
    assert server["command"] == "uvx"
    assert server["enabled"] is True
    # md2ui-mcp-demo is md2ui's console-script name for its window server.
    assert server["args"] == ["--from", PIN, "md2ui-mcp-demo", "--fetch"]
    print("  ✓  the manifest names one enabled stdio server: the release, run by uvx")


def test_marketplace_points_at_the_plugin():
    marketplace = _json(ROOT / ".agents/plugins/marketplace.json")
    assert marketplace["name"] == "md2ui"
    (entry,) = marketplace["plugins"]
    assert entry["name"] == "md2ui", entry
    source = entry["source"]
    assert source == {"source": "local", "path": "./codex/plugins/md2ui"}
    assert (ROOT / source["path"]).resolve() == PACKAGE.resolve()
    assert entry["policy"] == {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }
    print("  ✓  the root marketplace lists one plugin, md2ui, and resolves it")


async def _listed_tools(cwd: str) -> set[str]:
    server = _server()
    params = StdioServerParameters(command=server["command"], args=server["args"], cwd=cwd)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return {tool.name for tool in (await session.list_tools()).tools}


def test_stdio_configuration_starts_the_real_server():
    with tempfile.TemporaryDirectory() as cwd:
        tools = asyncio.run(_listed_tools(cwd))
    assert tools == {
        "actions",
        "check",
        "feed",
        "guide",
        "history",
        "layout",
        "mark",
        "outline",
        "patch",
        "preview",
        "screenshot",
        "show",
        "showing",
        "status",
        "wait_for_event",
    }
    print("  ✓  the packaged stdio command starts md2ui with all fifteen tools")


TESTS = [
    test_manifest_names_one_local_stdio_server,
    test_marketplace_points_at_the_plugin,
    test_stdio_configuration_starts_the_real_server,
]


if __name__ == "__main__":
    print("Codex Packaging Tests")
    print("=" * 50)
    failed = 0
    for test in TESTS:
        try:
            test()
        except Exception as exc:
            print(f"  ✗  {test.__name__}: {exc!r}")
            failed += 1
    print("=" * 50)
    if failed:
        print(f"{failed} test(s) FAILED.")
        raise SystemExit(1)
