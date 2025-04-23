import type TemplaterPlugin from "templater-obsidian";
import type { Templater } from "./templater";

/**
 * Get selection, falling back to clipboard.
 */
export default async (): Promise<string> => {
  const tp = (
    (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
      .templater as Templater
  ).current_functions_object;
  return tp.file.selection() || (await navigator.clipboard.readText());
};
