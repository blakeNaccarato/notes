/**
 * Get time tracking entry for the selection or clipboard.
 */

import type TemplaterPlugin from "templater-obsidian";

export default async (): Promise<void> => {
  const tp = (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
    .templater.current_functions_object;
  const r = String.raw;
  const text: string = (
    tp.file.selection() || (await navigator.clipboard.readText())
  )
    // Replace Markdown-style links with link text
    .replace(/\[(?<linkText>[^\]]*)\]\([^)]*\)/g, "$<linkText>")
    // Get the desired time tracking entry substring
    .match(
      r`^` +
        r`(?:\s*-)?` + // Markdown-style bullet
        r`(?:\s*\[[^\]]?\])?` + // Markdown-style checkbox
        r`(?:.*#)?` + // Leading tags or header hashes, including the last `#`
        r`\s*` + // Leading whitespace
        // Consume characters up to emoji, newline, or end of string
        r`(?<timeTrackingEntry>(?:` +
        r`(?!⏫|⏬|⏳|⛔|✅|❌|➕|🏁|📅|🔁|🔺|🔼|🔽|🛫)` +
        r`.)*)`,
    )
    // Clean up the matched time tracking entry
    .groups.timeTrackingEntry.trim()
    .replace(/^\w/, (c: string) => c.toUpperCase());
  if (text) {
    await navigator.clipboard.writeText(text);
    new Notice(`Copied "${text}"`);
    return;
  }
  new Notice("Couldn't form time tracking entry from selection or clipboard");
};
