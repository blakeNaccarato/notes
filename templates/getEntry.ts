import type TemplaterPlugin from "templater-obsidian";
import type { Templater } from "./types";

/**
 * Get entry for selection or clipboard.
 */
export default async (): Promise<void> => {
  const idToken = "🆔";
  const idPart = String.raw`\d{4}-\d{2}-\d{2}T\d{6}[\+-]\d{4}|[\d\w]+`;
  const emptyParens = String.raw`\(\)`; // Possible in Obsidian Tasks output
  const obsidianTasksSymbols = String.raw`⏫|⏬|⏳|⛔|✅|❌|➕|🏁|📅|🔁|🔺|🔼|🔽|🛫`;
  // Replace Markdown-style links with link text
  let text: string = (
    await (
      (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
        .templater as Templater
    ).current_functions_object.user.getSelOrClip()
  ).replace(/\[(?<linkText>[^\]]*)\]\([^)]*\)/g, "$<linkText>");
  // Get entry
  const { entry, taskId, logId } = text.match(
    "^" + // Beginning of string
      String.raw`(?:\s*-)?` + // Markdown-style bullet
      String.raw`(?:\s*\[[^\]]?\])?` + // Markdown-style checkbox
      String.raw`(?<logId>\s*${idToken}\s*${idPart}:)?` + // Log ID
      "(?:s*.*#)?" + // Leading tags or header hashes, including the last `#`
      // Compose entry from consumed characters and optional task ID
      (String.raw`\s*(?<entry>` +
        // Recursively consume characters without capturing
        (String.raw`\s*(?:` +
          String.raw`(?!${idToken}|${emptyParens}|${obsidianTasksSymbols})` +
          "." + // Consume one character
          ")*") + // Repeat consumption until negative lookahead fails
        String.raw`\s*(?<taskId>${idToken}\s*${idPart})?` + // Task ID
        ")"),
  )?.groups as { entry?: string; logId?: string; taskId?: string };
  // Clean up the matched time tracking entry
  const sp = " ";
  text = (entry || text)
    .trim()
    .replace(/^\w/, (c: string) => c.toUpperCase())
    .concat(!taskId && logId ? `${sp}${logId}` : "");
  // Write the result to the clipboard
  if (!text) {
    new Notice("Couldn't form time tracking entry from selection or clipboard");
  }
  await navigator.clipboard.writeText(text);
  new Notice(`Copied "${text}"`);
};
