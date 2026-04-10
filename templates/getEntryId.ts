import type { App } from "./types";

/**
 * Get entry ID for selection or clipboard.
 */
export default async (): Promise<void> => {
  const { entryId } = await (app as App).plugins
    .getPlugin("templater-obsidian")
    .templater.current_functions_object.user.getEntryGroups();
  if (!entryId) {
    new Notice("Couldn't form entry ID from selection or clipboard");
    return;
  }
  await navigator.clipboard.writeText(entryId);
  new Notice(`Copied "${entryId}"`);
};
