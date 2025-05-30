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
  const id = String.raw`🆔 \d{4}-\d{2}-\d{2}T\d{6}-\d{4}`;
  // Replace Markdown-style links with link text
  let text: string = (await tp.user.getSelOrClip()).replace(
    /\[(?<linkText>[^\]]*)\]\([^)]*\)/g,
    "$<linkText>",
  );
  // Match the time tracking entry
  const groups = text.match(
    String.raw`^` +
      String.raw`(?:\s*-)?` + // Markdown-style bullet
      String.raw`(?:\s*\[[^\]]?\])?` + // Markdown-style checkbox
      String.raw`(?:\s*(?<logId>${id}):)?` + // Log timestamp
      String.raw`(?:.*#)?\s*` + // Leading tags or header hashes, including the last `#`
      String.raw`(?<timeTrackingEntry>(?:` + // Get time tracking entry
      (String.raw`(?:(?<taskId>${id})\s*)?` + // Task timestamp
        // Consume characters up to emoji, newline, or end of string
        String.raw`(?!⏫|⏬|⏳|⛔|✅|❌|➕|🏁|📅|🔁|🔺|🔼|🔽|🛫)`) +
      String.raw`.)*)`,
  )?.groups as { timeTrackingEntry?: string; logId?: string; taskId?: string };
  // Clean up the matched time tracking entry
  text = (groups?.timeTrackingEntry ? groups.timeTrackingEntry : text)
    .trim()
    .replace(/^\w/, (c: string) => c.toUpperCase())
    .concat(!groups?.taskId && groups?.logId ? ` ${groups.logId}` : "");
  // Write the result to the clipboard
  if (text) {
    await navigator.clipboard.writeText(text);
    new Notice(`Copied "${text}"`);
    return;
  }
  new Notice("Couldn't form time tracking entry from selection or clipboard");
};
