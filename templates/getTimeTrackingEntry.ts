import type TemplaterPlugin from "templater-obsidian";
import type { Templater } from "./types";

/**
 * Get time tracking entry for selection or clipboard.
 */
export default async (): Promise<void> => {
  const tp = (
    (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
      .templater as Templater
  ).current_functions_object;
  const text: string = (
    (
      (await tp.user.getSelOrClip())
        // Replace Markdown-style links with link text
        .replace(/\[(?<linkText>[^\]]*)\]\([^)]*\)/g, "$<linkText>")
        // Get the desired time tracking entry substring
        .match(
          String.raw`^` +
            String.raw`(?:\s*-)?` + // Markdown-style bullet
            String.raw`(?:\s*\[[^\]]?\])?` + // Markdown-style checkbox
            String.raw`(?:.*#)?` + // Leading tags or header hashes, including the last `#`
            String.raw`\s*` + // Leading whitespace
            // Consume characters up to emoji, newline, or end of string
            String.raw`(?<timeTrackingEntry>(?:` +
            String.raw`(?!⏫|⏬|⏳|⛔|✅|❌|➕|🏁|📅|🔁|🔺|🔼|🔽|🛫)` +
            String.raw`.)*)`,
        ) as RegExpMatchArray
    ).groups as { timeTrackingEntry: string }
  )["timeTrackingEntry"]
    // Clean up the matched time tracking entry
    .trim()
    .replace(/^\w/, (c: string) => c.toUpperCase());
  // Write the result to the clipboard
  if (text) {
    await navigator.clipboard.writeText(text);
    new Notice(`Copied "${text}"`);
    return;
  }
  new Notice("Couldn't form time tracking entry from selection or clipboard");
};
