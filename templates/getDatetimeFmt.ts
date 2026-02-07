import type { Templater, TemplaterPlugin } from "./types";

/**
 * Get datetime format.
 */
export default (): string => {
  // Can't use moment().toISOString() because we use a non-standard time
  // delimiter. Moment is a popular JavaScript library built in to Obsidian, so we
  // access it via Templater's Obsidian namespace. See:
  //
  // - https://silentvoid13.github.io/Templater/internal-functions/internal-modules/obsidian-module.html#obsidian-module
  // - https://github.com/obsidianmd/obsidian-api/blob/master/obsidian.d.ts
  // - https://docs.obsidian.md/Plugins/Events
  // - https://momentjs.com/docs/#/displaying/as-iso-string/
  //
  const { user } = (
    (app.plugins.getPlugin("templater-obsidian") as TemplaterPlugin)
      .templater as Templater
  ).current_functions_object;
  return `${user.getDateFmt()}T${user.getTimeFmt()}`;
};
