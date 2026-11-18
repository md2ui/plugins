---
name: md2ui
description: Show replies in the local native md2ui window and hear its clicks and typed messages. Use when the md2ui tools are connected and the user asks to open md2ui or show an answer there.
---

# Answer through md2ui

The `show` tool is the reply, displayed in the user's native md2ui window. Send
the same ordinary Markdown that would otherwise be the chat answer. Do not turn
the request into a description of a UI.

## Required connection

Proceed only when `guide`, `show`, and `wait_for_event` are callable in the
current conversation. If any is unavailable, stop and tell the user that the
md2ui MCP backend is not connected to this conversation. Do not inspect the
filesystem, application inventory, repository, configuration, or shell to find
or launch an alternative runtime. Do not substitute computer use or UI
automation for the missing MCP tools.

## The loop

The md2ui server's instructions say how to answer, listen and end your turn, and
every result says what comes next: follow them.

The window is local: never claim that a hosted or web-only session can open it.
