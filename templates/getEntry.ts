import type TemplaterPlugin from "templater-obsidian";
import type { Templater } from "./types";

/**
 * Get entry for selection or clipboard.
 */
export default async (): Promise<void> => {
  const { entry, logId, taskId } = await (
    (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
      .templater as Templater
  ).current_functions_object.user.getEntryGroups();
  const sp = " ";
  const text = entry
    .trim()
    .replace(/^\w/, (c: string) => c.toUpperCase())
    .concat(!taskId && logId ? `${sp}${logId}` : "");
  if (!text) {
    new Notice("Couldn't form time tracking entry from selection or clipboard");
  }
  await navigator.clipboard.writeText(text);
  new Notice(`Copied "${text}"`);
};
