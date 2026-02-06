import type TemplaterPlugin from "templater-obsidian";
import type { Templater } from "./types";

/**
 * Get entry match object for selection or clipboard.
 */
export default async (): Promise<{
  entry: string;
  logId?: string;
  taskId?: string;
  entryId?: string;
}> => {
  const idToken = "🆔";
  const idPart = String.raw`\d{4}-\d{2}-\d{2}T\d{6}[\+-]\d{4}|[\d\w]+`;
  const emptyParens = String.raw`\(\)`; // Possible in Obsidian Tasks output
  const obsidianTasksSymbols = String.raw`⏫|⏬|⏳|⛔|✅|❌|➕|🏁|📅|🔁|🔺|🔼|🔽|🛫`;
  // Replace Markdown-style links with link text
  // Get entry
  return (
    await (
      (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
        .templater as Templater
    ).current_functions_object.user.getSelOrClip()
  )
    .replace(/\[(?<linkText>[^\]]*)\]\([^)]*\)/g, "$<linkText>")
    .match(
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
          String.raw`\s*(?<taskId>${idToken}\s*(?<entryId>${idPart}))?` + // Task ID
          ")"),
    )?.groups as { entry: string; logId?: string; taskId?: string; entryId?: string };
};
