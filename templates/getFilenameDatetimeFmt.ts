import type TemplaterPlugin from "templater-obsidian";
import type { Templater } from ".";

/**
 * Get modified datetime format that is legal in filenames.
 */
export default (): string => {
  return `${(
    (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
      .templater as Templater
  ).current_functions_object.user.getDatetimeFmt()}`.replaceAll(":", "");
};
