# md2ui demo for ChatGPT Desktop and Codex

This plugin is a Desktop-only OpenAI plugin that runs md2ui's demo server,
`md2ui-mcp-demo`, over stdio, from the published package. The repository's
marketplace, `.agents/plugins/marketplace.json` at its root, lists it. The same
package is available to locally running ChatGPT Work and Codex conversations in
the ChatGPT desktop app. The native
Python window opens on the first `show` tool call, connects to the MCP process
over loopback WebSocket, and returns clicks or typed prompts to the conversation.

The package uses the supported Codex compatibility layout:
`.codex-plugin/plugin.json` plus `.mcp.json`, the layout the plugin scaffold
generates and the local MCP plugins bundled with ChatGPT Desktop use. A hosted
or web-only process cannot display this native window on the user's Mac.

## Requirements

[uv](https://docs.astral.sh/uv/) on the `PATH` the host starts servers with. The
MCP manifest (`plugins/md2ui-demo/.mcp.json`) runs
`uvx --from md2ui==0.1.0a1 md2ui-mcp-demo --fetch`; the first start downloads
md2ui. The plugin has no settings: the server uses a `THEME.md` in the folder it
starts in, else md2ui's default theme. To use another theme, add
`"--theme", "/path/to/THEME.md"` to the manifest's `args`, then reinstall the
plugin.

## Add the marketplace

```sh
codex plugin marketplace add md2ui/plugins
```

This registers the marketplace only in the current user's local Codex/ChatGPT
Desktop configuration. It does not publish the plugin to a workspace or submit
it to the public Plugins Directory. Installing the plugin from this source
creates a local cached copy under `~/.codex/plugins/cache/`.

To unregister the marketplace later:

```sh
codex plugin marketplace remove md2ui
```

Restart the ChatGPT desktop app, select the **md2ui** source in Plugins,
and install **md2ui demo**. Start a new conversation after installing or after
updating the plugin; existing conversations do not reload MCP tools. When the
package version changes, uninstall and reinstall the plugin so Desktop replaces
its cached copy.

In a new local Codex conversation in the desktop app, type `@` and select
**md2ui demo**, then ask it to “open md2ui” or show an answer there so it calls
`show`. The window does not open during installation.

If ChatGPT says that `show`, `guide`, or `wait_for_event` is unavailable, stop
that conversation rather than allowing it to search for another local runtime.
Confirm the plugin is enabled, restart ChatGPT Desktop, and test from a new
conversation. The packaged skill explicitly forbids filesystem, application
inventory, shell, and UI-automation fallbacks when the MCP tools are missing.

For a startup check, run:

```sh
codex plugin list
codex mcp list
```

The plugin should be enabled and `md2ui-demo` should be listed as an enabled
stdio server. ChatGPT Desktop logs are under
`~/Library/Logs/com.openai.codex/` on macOS; a healthy attachment records an
`md2ui-demo` transition from `starting` to `ready`. If the conversation sees the
skill but the log has no startup transition, the client did not attach the MCP
backend to that conversation. Match the startup event to the conversation you
are testing. A `ready` event in a Codex thread only verifies that thread.

In ChatGPT Work, the plugin can be visible while its tools are unavailable.
If the affected Work conversation has no `md2ui-demo` startup event, check the
Desktop log for local Work executor staging errors. Use a local Codex conversation
in the desktop app to test the plugin while Work attachment is unresolved.
