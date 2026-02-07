import type { Templater, TemplaterPlugin } from "./types";

/**
 * Whether the current template was invoked from the "Templater: Create New Note From Template" command.
 */
export default (): boolean => {
  const tp = (
    (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
      .templater as Templater
  ).current_functions_object;
  return Boolean(tp.file.content || tp.file.path(true) != "Untitled.md");
};
