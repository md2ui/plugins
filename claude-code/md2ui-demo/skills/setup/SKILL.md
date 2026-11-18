---
name: setup
description: Fetch the font files a custom md2ui theme names that md2ui cannot fetch itself. Run once per theme, or when md2ui reports "[fonts] not found".
disable-model-invocation: true
---

# Set up md2ui's theme fonts

The plugin runs the published md2ui (`uvx --from md2ui==0.1.0a1`) with the theme
`${user_config.theme}`; an empty theme means a `THEME.md` in the project's folder, else
md2ui's default theme. md2ui fetches the fonts its own lock names (Inter, IBM Plex Mono and
the other fonts of md2ui's themes) on first use, verified against the lock. A font a custom
theme names as a local file that md2ui does not lock is a setup step, done here with the
user's approval. Ask before each download.

1. **uv.** Check `uvx --version`. If it is missing, tell the user how to install uv and stop.
2. **What is missing.** Write a short Markdown document to a temporary folder and render it
   with `uvx --from md2ui==0.1.0a1 md2ui render <file.md> --width 767 --theme <theme> --out
   <file.png>`. Each `[fonts] not found` line it prints names a font file still missing. None
   means there is nothing to do: say so and stop.
3. **Fetch each missing file.**
   - fetch `https://fonts.google.com/download/list?family=<Family>`, where `<Family>` is the
     family the file belongs to (`Inter_18pt-Regular.ttf` belongs to `Inter`);
   - the reply is JSON after a first line of `)]}'`, when that line is present;
   - in `manifest.fileRefs`, take the entry whose `filename` ends with the missing file's
     name, and download its `url` to the exact path the theme names, relative to the
     theme's own folder, so the theme and its fonts stay together;
   - save the family's `OFL.txt`, from `manifest.files`, beside it.

   Use only `fonts.google.com` and `fonts.gstatic.com`. If a family is not on Google Fonts,
   say so and leave it.
4. **Check.** Render the document again: there must be no `[fonts] not found` line.

End with what was fetched, and anything still missing.
