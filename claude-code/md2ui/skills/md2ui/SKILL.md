---
name: md2ui
description: Write an answer as md2ui Markdown (plain Markdown that md2ui renders as UI) and check it with md2ui's tools before it is sent. Use when an answer is meant for an md2ui frontend.
---

# Writing for md2ui

md2ui renders your Markdown reply as UI. Writing for it is writing your reply, in plain
Markdown, and it is harmless: nothing in it runs.

1. Read the core note once, with the `guide` tool and no topic. It says what each element
   means and how to write it.
2. For one section of an answer (a status list, choices, an agenda, an inbox), call
   `guide("patterns")`, then read only the pattern you need.
3. Before the answer is sent: `check` lists authoring mistakes, `actions` lists what the
   answer offers the user, and `preview` shows it when you need to look.

The notes are also the server's resources, `md2ui://skills/<file>`.
