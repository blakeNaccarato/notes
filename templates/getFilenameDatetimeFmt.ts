import type { App } from "./types";

/**
 * Get modified datetime format that is legal in filenames.
 */
export default (): string => {
  return `${(app as App).plugins
    .getPlugin("templater-obsidian")
    .templater.current_functions_object.user.getDatetimeFmt()}`.replaceAll(":", "");
};
