import type TemplaterPlugin from "templater-obsidian";
import type { Templater } from ".";

/**
 * Get choice.
 *
 * @param choices Mapping of labels to values.
 * @param description Prompt/description shown to the user.
 */
export default async <T>(description: string, choices: Record<string, T>) => {
  return await (
    (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
      .templater as Templater
  ).current_functions_object.system.suggester(
    Object.keys(choices),
    Object.values(choices),
    true,
    description,
  );
};
