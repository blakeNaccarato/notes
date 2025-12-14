import type TemplaterPlugin from "templater-obsidian";
import type { Templater } from "./types";

/**
 * Get entry ID for selection or clipboard.
 */
export default async (): Promise<void> => {
  const idToken = "🆔";
  const idPart = String.raw`\d{4}-\d{2}-\d{2}T\d{6}[\+-]\d{4}|[\d\w]+`;
  const emptyParens = String.raw`\(\)`; // Possible in Obsidian Tasks output
  const obsidianTasksSymbols = String.raw`⏫|⏬|⏳|⛔|✅|❌|➕|🏁|📅|🔁|🔺|🔼|🔽|🛫`;
  // Get entry ID
  const { entryId } = (
    await (
      (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
        .templater as Templater
    ).current_functions_object.user.getSelOrClip()
  )
    // Strip links, helps find ID for older entries that only have ID in link text
    .replace(/\[(?<linkText>[^\]]*)\]\([^)]*\)/g, "$<linkText>")
    // Match the entry
    .match(
      "^" + // Beginning of string
        String.raw`(?:\s*-)?` + // Markdown-style bullet
        String.raw`(?:\s*\[[^\]]?\])?` + // Markdown-style checkbox
        String.raw`(?:\s*${idToken}\s*${idPart}:)?` + // Log ID
        "(?:s*.*#)?" + // Leading tags or header hashes, including the last `#`
        // Compose entry from consumed characters and optional task ID
        (String.raw`\s*(?:` +
          // Recursively consume characters without capturing
          (String.raw`\s*(?:` +
            String.raw`(?!${idToken}|${emptyParens}|${obsidianTasksSymbols})` +
            "." + // Consume one character
            ")*") + // Repeat consumption until negative lookahead fails
          String.raw`\s*(?:${idToken}\s*(?<entryId>${idPart}))?` + // Task ID
          ")"),
    )?.groups as { entryId?: string };
  if (!entryId) {
    new Notice("Couldn't form entry ID from selection or clipboard");
    return;
  }
  await navigator.clipboard.writeText(entryId);
  new Notice(`Copied "${entryId}"`);
  return;
};
