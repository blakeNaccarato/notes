import type { App } from "./types";

/**
 * Whether the current template was invoked from the "Templater: Create New Note From Template" command.
 */
export default (): boolean => {
  const tp = (app as App).plugins.getPlugin("templater-obsidian").templater
    .current_functions_object;
  return tp.file.path(true) === "Untitled.md" && !tp.file.content;
};
