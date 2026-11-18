# md2ui plugins

The host packages of md2ui, which shows an agent's answers as UI in a native window on your
computer and returns your clicks, with authoring tools to check and preview an answer: the
Claude Code plugin, the Claude Desktop extension, and the local OpenAI plugin for ChatGPT
Desktop and Codex. Every host installs one plugin, `md2ui`.

md2ui is experimental: anything may change between 0.x releases.

| Path | What |
|---|---|
| `.claude-plugin/marketplace.json` | The Claude Code marketplace, `md2ui`, listing the plugin in `claude-code/` |
| `claude-code/md2ui/` | The Claude Code plugin, `md2ui`: the window and the authoring tools |
| `claude-desktop/md2ui/` | The Claude Desktop extension (`.mcpb`): a manifest and a launcher |
| `.agents/plugins/marketplace.json` | The ChatGPT Desktop and Codex marketplace, `md2ui`, listing the plugin in `codex/` |
| `codex/` | The Desktop-only OpenAI plugin for ChatGPT Desktop and Codex; its own notes are in `codex/README.md` |
| `tests/` | The packages' tests |

Every package carries the md2ui logo as its icon, a copy inside its own folder because each
host reads it only from there: `assets/icon.png` in the Claude Code plugin and in the OpenAI
plugin, and `icon.png` in the Desktop extension. All three are the same 512 px square file, as
Anthropic's plugin directory requires and Claude Desktop recommends. Replace all three together.

## Install: every package runs the published md2ui

Each package holds host metadata, thin skills that point at md2ui's `guide`, and at most a
launcher; never md2ui's code (md2ui ADR-605). Each runs md2ui's server from PyPI with
`uvx --from md2ui==0.1.0a1`, so it needs [uv](https://docs.astral.sh/uv/) and Python 3.13 or
later (uv fetches one when none is installed). The first start downloads md2ui; later ones
start from uv's cache. With `--fetch`, the server downloads the fonts md2ui locks on first
use, into `~/.cache/md2ui/fonts`.

On Linux, md2ui also needs the system libraries skia-python loads (libEGL, libGL and
fontconfig); on Debian or Ubuntu:

```
sudo apt install libgl1 libegl1 libfontconfig1
```

**Claude Code**, from this repository's marketplace:

```
/plugin marketplace add md2ui/plugins
/plugin install md2ui@md2ui
```

While Claude works, the window says what it is doing, from a hook before each tool call: a
Bash call's description, else the tool and a file's name, never a command or a path. The
**Working line** setting turns it off. `/md2ui:setup` fetches the font files a custom theme
names that md2ui does not lock, asking before each download. By hand instead (`md2ui-mcp-demo`
is md2ui's own name for its window server):

```
claude mcp add md2ui -- uvx --from md2ui==0.1.0a1 md2ui-mcp-demo --fetch --theme /path/to/THEME.md
```

**Claude Desktop**, as an extension (macOS only): download `md2ui.mcpb` from the
[latest release](https://github.com/md2ui/plugins/releases/latest) and open it in Claude
Desktop; in the extension's settings you may choose a THEME.md.

To build it yourself (needs Node for `npx`):

```
npx @anthropic-ai/mcpb validate claude-desktop/md2ui/manifest.json
npx @anthropic-ai/mcpb pack claude-desktop/md2ui /tmp/md2ui.mcpb
```

The `.mcpb` is a build output: never commit it. The release workflow builds it from
`claude-desktop/md2ui/`, which names the md2ui release the launcher runs.

**ChatGPT Desktop and Codex** use the same Desktop-only plugin and native MCP server:

```sh
codex plugin marketplace add md2ui/plugins
```

Or install it from the command line: `codex plugin add md2ui@md2ui`. In the ChatGPT desktop
app, restart it, open Plugins, choose the **md2ui** source, and install **md2ui**. Start a new
local Codex conversation in the desktop app, select the plugin with `@md2ui`, and ask it to
open md2ui. Web and hosted conversations cannot open
a native window on your computer. See [`codex/README.md`](codex/README.md) for cache refresh
steps and ChatGPT Work attachment diagnostics.

> **ChatGPT Desktop users:** ChatGPT Work may show “Some tools are currently
> unavailable” even when **md2ui** is installed and visible. In the same
> desktop app, start a new local **Codex** conversation, select `@md2ui`,
> and ask it to open md2ui. Native window rendering has been verified in local
> Codex. ChatGPT Work tool attachment is still unresolved.

**A pinned release.** The commands above follow the repository's `main`. To install one
release instead, add the marketplace at its tag:

```
/plugin marketplace add md2ui/plugins#v0.1.0-alpha.3
codex plugin marketplace add md2ui/plugins@v0.1.0-alpha.3
```

The first is Claude Code's, the second Codex's and ChatGPT Desktop's.

## Upgrading from 0.1.0-alpha.1 or 0.1.0-alpha.2

Those releases named the window plugin `md2ui-demo`, and Claude Code had a second plugin,
`md2ui`, with the authoring tools alone. From 0.1.0-alpha.3 there is one plugin, `md2ui`, on
every host, with the window and the authoring tools. Remove the old one and install the new:

**Claude Code:**

```
/plugin uninstall md2ui-demo@md2ui
/plugin marketplace update md2ui
/plugin install md2ui@md2ui
```

If you had installed the authoring-only `md2ui@md2ui`, the last two lines replace it.

**ChatGPT Desktop and Codex:**

```sh
codex plugin remove md2ui-demo@md2ui
codex plugin marketplace upgrade md2ui
codex plugin add md2ui@md2ui
```

Then restart the ChatGPT desktop app and start a new conversation.

**Claude Desktop:** remove the old **md2ui demo** extension in Claude Desktop's extension
settings, then download `md2ui.mcpb` from the
[latest release](https://github.com/md2ui/plugins/releases/latest) and open it.

## Options

**Claude Code** (`claude-code/md2ui/.claude-plugin/plugin.json`, `userConfig`), set with
`/plugin configure` or in `/config`:

| Option | Type | Default | Effect | Example |
|---|---|---|---|---|
| THEME.md (`theme`) | file | empty | The theme the window and previews draw with; empty uses a `THEME.md` in the project's folder, else md2ui's default theme | `~/themes/brand/THEME.md` |
| Working line (`working_line`) | boolean | `true` | While Claude works, the window shows a label of each tool call (a Bash call's description, else the tool and a file's name, never a command or a path); `false` shows only the working animation | `false` |

**Claude Desktop** (`claude-desktop/md2ui/manifest.json`, `user_config`), in the
extension's settings:

| Option | Type | Default | Effect | Example |
|---|---|---|---|---|
| THEME.md (`theme`) | file | empty | The theme the window draws with; empty uses md2ui's default theme | `~/themes/brand/THEME.md` |

There is no Working line option in Claude Desktop.

**ChatGPT Desktop and Codex** have no options: the plugin offers no settings. The server uses
a `THEME.md` in the folder it starts in, else md2ui's default theme
(`codex/README.md`).

## Tests

The tests run against the md2ui release the packages name, and the live ones start the
servers with `uvx`, as the hosts do:

```
uv run --python 3.13 --with md2ui==0.1.0a1 python tests/packaging_tests.py
uv run --python 3.13 --with md2ui==0.1.0a1 python tests/codex_packaging_tests.py
```

## A new md2ui release

The release is named in each package: `plugin.json`, `hooks/hooks.json` and the `setup`
skill under `claude-code/md2ui/`, the Desktop launcher and its manifest's description, and `codex/`'s
`.mcp.json`. Change all of them together; the tests fail while any names a release other than
the one they run with.

Any change that ships, a new md2ui release or not, is a new plugins release: raise the version
in the three package manifests (`claude-code/md2ui/`'s `plugin.json`, the Desktop
`manifest.json`, `codex/`'s `plugin.json`) together. That version is the plugins' own, apart
from md2ui's: plugins `0.1.0-alpha.3` still run `md2ui==0.1.0a1`.

Then push a tag `v<version>` (the packages' version, e.g. `v0.1.0-alpha.3`):
`.github/workflows/release.yml` checks the tag matches every package, runs the tests against
the pinned md2ui, builds the Claude Desktop extension and attaches it to a GitHub Release.
`check.yml` runs the same tests on every push.
