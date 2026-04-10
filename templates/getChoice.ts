import type { App } from "./types";

/**
 * Get choice.
 *
 * @param choices Mapping of labels to values.
 * @param description Prompt/description shown to the user.
 */
export default async <T>(description: string, choices: Record<string, T>) => {
  return await (app as App).plugins
    .getPlugin("templater-obsidian")
    .templater.current_functions_object.system.suggester(
      Object.keys(choices),
      Object.values(choices),
      true,
      description,
    );
};
