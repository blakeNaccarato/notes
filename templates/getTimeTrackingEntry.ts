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
  // Replace Markdown-style links with link text
  let text: string = (await tp.user.getSelOrClip()).replace(
    /\[(?<linkText>[^\]]*)\]\([^)]*\)/g,
    "$<linkText>",
  );
  // Match the time tracking entry
  const idToken = "🆔";
  const id = String.raw`${idToken}\s*\d{4}-\d{2}-\d{2}T\d{6}[\+-]\d{4}`;
  const emptyParens = String.raw`\(\)`; // Possible in Obsidian Tasks output
  const groups = text.match(
    "^" + // Beginning of string
      String.raw`(?:\s*-)?` + // Markdown-style bullet
      String.raw`(?:\s*\[[^\]]?\])?` + // Markdown-style checkbox
      String.raw`(?:\s*(?<logId>${id}):)?` + // Log ID
      "(?:s*.*#)?" + // Leading tags or header hashes, including the last `#`
      // Compose entry from consumed characters and optional task ID
      (String.raw`\s*(?<timeTrackingEntry>` +
        // Recursively consume characters without capturing
        (String.raw`\s*(?:` +
          String.raw`(?!${idToken}|${emptyParens}|⏫|⏬|⏳|⛔|✅|❌|➕|🏁|📅|🔁|🔺|🔼|🔽|🛫)` +
          "." + // Consume one character
          ")*") + // Repeat consumption until negative lookahead fails
        String.raw`\s*(?<taskId>${id})?` + // Task ID
        ")"),
  )?.groups as {
    timeTrackingEntry?: string;
    logId?: string;
    taskId?: string;
  };
  // Clean up the matched time tracking entry
  const sp = " ";
  text = (groups.timeTrackingEntry || text)
    .trim()
    .replace(/^\w/, (c: string) => c.toUpperCase())
    .concat(!groups.taskId && groups.logId ? `${sp}${groups.logId}` : "");
  // Write the result to the clipboard
  if (text) {
    await navigator.clipboard.writeText(text);
    new Notice(`Copied "${text}"`);
    return;
  }
  new Notice("Couldn't form time tracking entry from selection or clipboard");
};
