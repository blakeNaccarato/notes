import type { Templater, TemplaterPlugin } from "./types";

/**
 * Whether the current template was invoked from the "Templater: Create New Note From Template" command.
 */
export default (): boolean => {
  const tp = (
    (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
      .templater as Templater
  ).current_functions_object;
  return tp.file.path(true) === "Untitled.md" && !tp.file.content;
};
