import type { App } from "./types";

/**
 * Get selection, falling back to clipboard.
 */
export default async (): Promise<string> => {
  const tp = (app as App).plugins.getPlugin("templater-obsidian").templater
    .current_functions_object;
  return tp.file.selection() || (await navigator.clipboard.readText());
};
