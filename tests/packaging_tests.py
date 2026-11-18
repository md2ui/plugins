"""
Unit tests for md2ui's Claude packages (md2ui ADR-605): the Claude Desktop
extension, a manifest and a launcher that start the demo server from the
published md2ui package; and the two Claude Code plugins, listed by the
marketplace at the repository's root, which run the authoring and demo shells
from that package too.

The bundle is built outside the repo (``npx @anthropic-ai/mcpb pack``), so these
tests are what keep its two files honest between builds. They run against the
md2ui release the packages name, installed where they run:

    uv run --python 3.13 --with md2ui==0.1.0a1 python tests/packaging_tests.py

Pinned here:

  * every package names one md2ui release, and it is the one installed here;
  * the manifest has MCPB's required fields, its entry point exists, and every
    ``${user_config.*}`` it substitutes is a declared setting;
  * the tools it lists are exactly the tools the demo server registers, so the
    listing Desktop shows cannot drift from the server;
  * the launcher's command is the README's hand registration, with ``--theme``
    only when a theme is set — an unset setting that arrives unsubstituted
    counts as unset — and a theme that is not a file is refused;
  * the marketplace at the root lists both plugins; each runs its own console
    script from the release and declares every setting it substitutes;
  * every plugin skill is named for its folder, and the two plugins' ``setup``
    skills are one text, kept as files because an installed plugin does not
    follow a symlink out of its own folder;
  * the demo plugin's working-line hook runs md2ui's hook script from the
    release in exec form, behind a boolean switch that is on by default.
"""

import asyncio
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from importlib import metadata
from pathlib import Path

from md2ui import mcp_demo
from md2ui.pipeline.render_settings import VIEW
from md2ui.utils.fetch_policy import POLICY

ROOT = Path(__file__).resolve().parent.parent
EXTENSION = ROOT / "claude-desktop" / "md2ui-demo"
MANIFEST = EXTENSION / "manifest.json"
LAUNCHER = EXTENSION / "server" / "launch.py"
REQUIRED = ("manifest_version", "name", "version", "description", "author", "server")
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
PLUGINS = ROOT / "claude-code"
# The release installed here, which every package must name.
PIN = f"md2ui=={metadata.version('md2ui')}"
# Each plugin's console script, and the module md2ui declares it for.
SCRIPTS = {"md2ui": "md2ui-mcp", "md2ui-demo": "md2ui-mcp-demo"}
HOOK_SCRIPT = "md2ui-demo-activity"


def _console_scripts() -> dict[str, str]:
    return {
        entry.name: entry.value
        for entry in metadata.distribution("md2ui").entry_points
        if entry.group == "console_scripts"
    }


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text())


def _launch(env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    clean = {k: v for k, v in os.environ.items() if not k.startswith("MD2UI_")}
    return subprocess.run(
        [sys.executable, str(LAUNCHER), *args],
        env=clean | env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_every_package_names_the_installed_release():
    texts = {
        path.relative_to(ROOT): path.read_text()
        for pattern in ("**/*.json", "**/.mcp.json", "**/launch.py")
        for path in ROOT.glob(pattern)
        if ".git" not in path.parts
    }
    named = {
        path: set(re.findall(r"md2ui==[0-9][0-9A-Za-z.+!-]*", text))
        for path, text in texts.items()
    }
    named = {path: pins for path, pins in named.items() if pins}
    assert len(named) == 6, sorted(map(str, named))
    wrong = {str(path): pins for path, pins in named.items() if pins != {PIN}}
    assert not wrong, (PIN, wrong)
    print(f"  ✓  {len(named)} package files name {PIN}, the release installed here")


def test_the_manifest_is_complete():
    manifest = _manifest()
    missing = [field for field in REQUIRED if field not in manifest]
    assert not missing, missing
    server = manifest["server"]
    assert server["type"] == "python", server
    assert (EXTENSION / server["entry_point"]).is_file(), server["entry_point"]
    used = set(re.findall(r"\$\{user_config\.(\w+)\}", json.dumps(server)))
    declared = set(manifest["user_config"])
    assert used == declared == {"theme"}, (used, declared)
    assert manifest["user_config"]["theme"]["required"] is False
    print("  ✓  required fields, an entry point on disk, every setting declared")


def test_the_listed_tools_are_the_servers():
    server, _demo = mcp_demo.build_demo_server(None, launch_window=False)
    try:
        registered = {t.name for t in asyncio.run(server.list_tools())}
    finally:
        POLICY.remote, VIEW.placeholder_images = True, False  # as an app left it
    listed = {tool["name"] for tool in _manifest()["tools"]}
    assert listed == registered, listed ^ registered
    print(f"  ✓  the manifest lists exactly the {len(listed)} tools the demo registers")


def test_the_launcher_runs_the_readme_command():
    ran = _launch({}, "--dry-run")
    assert ran.returncode == 0, ran.stderr
    command = shlex.split(ran.stdout)
    assert Path(command[0]).name == "uvx", command
    assert command[1:] == ["--from", PIN, "md2ui-mcp-demo", "--fetch"], command

    with tempfile.TemporaryDirectory() as tmp:
        theme = Path(tmp) / "THEME.md"
        theme.write_text("# Theme\n")
        ran = _launch({"MD2UI_THEME": str(theme)}, "--dry-run")
        assert shlex.split(ran.stdout)[-2:] == ["--theme", str(theme)], ran.stdout

    ran = _launch({"MD2UI_THEME": "${user_config.theme}"}, "--dry-run")
    assert ran.returncode == 0 and "--theme" not in ran.stdout, ran
    print(f"  ✓  uvx --from {PIN} md2ui-mcp-demo --fetch [--theme]")


def test_the_launcher_refuses_a_missing_theme():
    with tempfile.TemporaryDirectory() as tmp:
        ran = _launch({"MD2UI_THEME": str(Path(tmp) / "THEME.md")}, "--dry-run")
    assert ran.returncode == 2, ran
    assert "no such theme" in ran.stderr and not ran.stdout, ran
    print("  ✓  a theme that is not a file is refused, on stderr only")


def _plugins() -> dict[str, dict]:
    index = json.loads(MARKETPLACE.read_text())
    return {
        entry["name"]: json.loads(
            (ROOT / entry["source"] / ".claude-plugin" / "plugin.json").read_text()
        )
        for entry in index["plugins"]
    }


def test_each_plugin_runs_its_shell_from_the_release():
    plugins = _plugins()
    assert set(plugins) == set(SCRIPTS), set(plugins)
    scripts = _console_scripts()
    for name, plugin in plugins.items():
        assert plugin["name"] == name, plugin["name"]
        (server,) = plugin["mcpServers"].values()
        args = server["args"]
        assert server["command"] == "uvx", server
        assert args[:3] == ["--from", PIN, SCRIPTS[name]], args
        assert SCRIPTS[name] in scripts, (SCRIPTS[name], sorted(scripts))
        assert "--fetch" in args, (name, "a local install previews pictures")
        assert args[-2:] == ["--theme", "${user_config.theme}"], args
        used = set(re.findall(r"\$\{user_config\.(\w+)\}", json.dumps(server)))
        assert used <= set(plugin["userConfig"]), (name, used)
        theme = plugin["userConfig"]["theme"]
        assert theme["required"] is False and theme["default"] == "", theme
    print("  ✓  md2ui and md2ui-demo each run their console script from the release")


def test_the_plugin_skills_are_named_and_shared():
    skills = sorted(PLUGINS.glob("*/skills/*/SKILL.md"))
    for path in skills:
        inside = [p for p in (path, *path.parents) if p.is_relative_to(PLUGINS)]
        assert not any(p.is_symlink() for p in inside), path
        text = path.read_text()
        name = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
        assert name and name.group(1).strip() == path.parent.name, path
        assert re.search(r"^description:\s*\S", text, re.MULTILINE), path
    setups = {path.parent.parent.parent.name: path for path in skills if "setup" in path.parts}
    assert set(setups) == set(SCRIPTS), set(setups)
    assert len({path.read_text() for path in setups.values()}) == 1, "setup copies differ"
    print(f"  ✓  {len(skills)} plugin skills named; both plugins' setup is one text")


def test_the_demo_hook_posts_the_working_line_from_the_release():
    """The working line (md2ui ADR-613): a ``PreToolUse`` hook in exec form, as
    Claude Code requires of a command that substitutes ``${user_config.*}``,
    running md2ui's own hook script from the release, behind a boolean switch
    that is on by default. Run as Claude Code would, from a folder of its own, it
    exits 0 and says nothing when no window is there to post to."""
    plugin = _plugins()["md2ui-demo"]
    hooks_file = PLUGINS / "md2ui-demo" / "hooks" / "hooks.json"
    hooks = json.loads(hooks_file.read_text())
    ((entry,),) = [group["hooks"] for group in hooks["hooks"]["PreToolUse"]]
    assert set(hooks["hooks"]) == {"PreToolUse"}, set(hooks["hooks"])
    assert entry["command"] == "uvx", entry
    args = entry["args"]
    assert args == ["--from", PIN, HOOK_SCRIPT, "${user_config.working_line}"], args
    assert HOOK_SCRIPT in _console_scripts()
    used = set(re.findall(r"\$\{user_config\.(\w+)\}", json.dumps(entry)))
    assert used == {"working_line"} <= set(plugin["userConfig"]), used
    switch = plugin["userConfig"]["working_line"]
    assert switch["type"] == "boolean" and switch["default"] is True, switch
    call = {"session_id": "no-such-session", "tool_name": "Read", "tool_input": {}}
    with tempfile.TemporaryDirectory() as cwd:
        for value in ("true", "false"):
            ran = subprocess.run(
                ["uvx", *[a.replace("${user_config.working_line}", value) for a in args]],
                input=json.dumps(call),
                capture_output=True,
                text=True,
                timeout=120,
                cwd=cwd,
            )
            assert (ran.returncode, ran.stdout) == (0, ""), (value, ran)
    print("  ✓  the demo's hook runs md2ui's working line from the release, switchable")


TESTS = [
    test_every_package_names_the_installed_release,
    test_the_manifest_is_complete,
    test_the_listed_tools_are_the_servers,
    test_the_launcher_runs_the_readme_command,
    test_the_launcher_refuses_a_missing_theme,
    test_each_plugin_runs_its_shell_from_the_release,
    test_the_plugin_skills_are_named_and_shared,
    test_the_demo_hook_posts_the_working_line_from_the_release,
]

if __name__ == "__main__":
    print("Packaging Tests")
    print("=" * 50)
    failed = 0
    for test in TESTS:
        try:
            test()
        except Exception as e:
            print(f"  ✗  {test.__name__}: {e!r}")
            failed += 1
    print("=" * 50)
    if failed:
        print(f"{failed} test(s) FAILED.")
        raise SystemExit(1)
